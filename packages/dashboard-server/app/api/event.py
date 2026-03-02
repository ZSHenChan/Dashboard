import os, json, asyncio
import logging
from typing import List, Literal
from pydantic import BaseModel, Field
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
import redis.asyncio as redis
from app.api.dependencies import get_redis_client
from app.utils.log_handlers import session_logger_with_task
from core.config import config
from core.context import get_request_id
from .logger import log_training_data

event_router = APIRouter(prefix="/event", tags=["Event"])

server_logger = logging.getLogger(config.CENTRAL_LOGGER_NAME)

class ReplyMetadata(BaseModel):
    label: str = Field(..., description="The UI label, e.g., 'Agree', or 'Custom'")
    sentiment: Literal["positive", "negative", "neutral"]
    is_custom: bool = Field(default=False, description="True if the user typed manually")

class ReplyRequest(BaseModel):
    chat_id: int
    text: List[str]
    card_id: str
    meta: ReplyMetadata

class MuteRequest(BaseModel):
    chat_id: int
    card_id: str

@event_router.post("/reply")
async def send_reply(req: ReplyRequest, background_tasks: BackgroundTasks, cache: redis.Redis = Depends(get_redis_client)):
    with session_logger_with_task(background_tasks) as logger:
        command = {
            "action": "reply",
            "chat_id": req.chat_id,
            "text": req.text,
        }

        raw_json = await cache.hget("dashboard:items", req.card_id)
        
        if raw_json:
            card_data = json.loads(raw_json)
            
            history_context = card_data.get("conversation_history", "")
            
            log_training_data(
                history=history_context, 
                chosen_reply=req.text,
                metadata=req.meta.model_dump()
            )
        
        await cache.publish("userbot:commands", json.dumps(command))
        
        await cache.hdel("dashboard:items", req.card_id)

        await cache.hdel("dashboard:active_chats", req.chat_id)
        
        return {"status": "sent", "text": req.text}

@event_router.post("/mute")
async def mute_chat_id(req: MuteRequest, background_tasks: BackgroundTasks, cache: redis.Redis = Depends(get_redis_client)):
    with session_logger_with_task(background_tasks) as logger:
        await cache.sadd("userbot:omit", req.chat_id)

        await cache.hdel("dashboard:items", req.card_id)

        await cache.hdel("dashboard:active_chats", req.chat_id)
        
        return {"status": "success"}

@event_router.get("/notifications")
async def get_notifications(background_tasks: BackgroundTasks, cache: redis.Redis = Depends(get_redis_client)):
    with session_logger_with_task(background_tasks) as logger:
        all_items = await cache.hgetall("dashboard:items")
        
        parsed_list = [json.loads(val) for val in all_items.values()]
        
        parsed_list.sort(key=lambda x: x['timestamp'], reverse=True)

        return parsed_list


@event_router.get("/stream")
async def stream_events(request: Request, cache: redis.Redis = Depends(get_redis_client)):

    req_id = get_request_id()
    server_logger.info("Stream Connected for user %s", request.client.host)

    async def event_generator():
        # Create a PubSub listener
        pubsub = cache.pubsub()
        await pubsub.subscribe("dashboard:events")
        
        try:
            async for message in pubsub.listen():
                # 'listen' gives us subscription messages too, ignore them
                if message["type"] == "message":
                    payload = message["data"]
                    yield f"data: {payload}\n\n"
                    print('Sent stream')
        except asyncio.CancelledError:
            server_logger.info("Stream Disconnected for ID: %s", req_id)
            await pubsub.unsubscribe("dashboard:events")
        except Exception as e:
            server_logger.error("Stream Error for ID %s: %s", req_id, e)
            raise

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@event_router.delete("/notifications/{card_id}")
async def delete_notification(card_id: str, background_tasks: BackgroundTasks, cache: redis.Redis = Depends(get_redis_client)):

    with session_logger_with_task(background_tasks) as logger:
        raw_json = await cache.hget("dashboard:items", card_id)
        
        if raw_json:
            data = json.loads(raw_json)
            chat_id = data.get('chat_id')
            
            if chat_id:
                await cache.hdel("dashboard:active_chats", str(chat_id))

        deleted_count = await cache.hdel("dashboard:items", card_id)

        return {"deleted": deleted_count > 0}

