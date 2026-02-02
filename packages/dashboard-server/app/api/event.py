import os, json, asyncio
import logging
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from core.config import config
from fastapi import APIRouter, Depends, Query, FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi import BackgroundTasks
from .logger import log_training_data
from core.redis_db import r
from core.context import get_request_id
from app.logging_config import SensitiveDataFilter
from app.utils.log_handlers import session_logger_with_task

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

@event_router.post("/reply")
async def send_reply(req: ReplyRequest, background_tasks: BackgroundTasks):
    with session_logger_with_task(background_tasks) as logger:
        command = {
            "action": "reply",
            "chat_id": req.chat_id,
            "text": req.text,
        }

        raw_json = await r.hget("dashboard:items", req.card_id)
        
        if raw_json:
            card_data = json.loads(raw_json)
            detected_sentiment = "custom"
            
            history_context = card_data.get("conversation_history", "")
            
            log_training_data(
                history=history_context, 
                chosen_reply=req.text,
                metadata=req.meta.model_dump()
            )
        
        # 2. Publish to Redis (The Userbot hears this instantly)
        await r.publish("userbot:commands", json.dumps(command))
        
        # 3. Cleanup: Remove the card from the Dashboard since we handled it
        await r.hdel("dashboard:items", req.card_id)

        await r.hdel("dashboard:active_chats", req.chat_id)
        
        logger.info(f"Processed reply for chat id {req.chat_id}")

        return {"status": "sent", "text": req.text}


@event_router.get("/notifications")
async def get_notifications(background_tasks: BackgroundTasks):
    with session_logger_with_task(background_tasks) as logger:
        all_items = await r.hgetall("dashboard:items")
        
        parsed_list = [json.loads(val) for val in all_items.values()]
        
        parsed_list.sort(key=lambda x: x['timestamp'], reverse=True)

        logger.info(f"Retrieved {len(parsed_list)} notifications.")

        return parsed_list


# 2. LIVE STREAM: Listen for NEW updates
@event_router.get("/stream")
async def stream_events(request: Request):

    req_id = get_request_id()
    server_logger.info(f"Stream Connected for user {request.client.host}")

    async def event_generator():
        # Create a PubSub listener
        pubsub = r.pubsub()
        await pubsub.subscribe("dashboard:events")
        
        try:
            async for message in pubsub.listen():
                # 'listen' gives us subscription messages too, ignore them
                if message["type"] == "message":
                    payload = message["data"]
                    yield f"data: {payload}\n\n"
                    print('Sent stream')
        except asyncio.CancelledError:
            server_logger.info(f"Stream Disconnected for ID: {req_id}")
            await pubsub.unsubscribe("dashboard:events")
        except Exception as e:
            server_logger.error(f"Stream Error for ID {req_id}: {e}")
            raise

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# 3. ACTION TAKEN: Delete the item
@event_router.delete("/notifications/{card_id}")
async def delete_notification(card_id: str, background_tasks: BackgroundTasks):

    with session_logger_with_task(background_tasks) as logger:
        raw_json = await r.hget("dashboard:items", card_id)
        
        if raw_json:
            data = json.loads(raw_json)
            chat_id = data.get('chat_id')
            
            # 2. Remove from Index
            if chat_id:
                await r.hdel("dashboard:active_chats", str(chat_id))

        # 3. Remove from Main Storage
        deleted_count = await r.hdel("dashboard:items", card_id)

        logger.info(f'Deleted card {card_id}')

        return {"deleted": deleted_count > 0}

