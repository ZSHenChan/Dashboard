import os, json, asyncio
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from core.config import config
from fastapi import APIRouter, Depends, Query, FastAPI, Request
from fastapi.responses import StreamingResponse
import redis.asyncio as redis
from .logger import log_training_data

event_router = APIRouter(prefix="/event", tags=["Event"])

r = redis.Redis(host=config.REDIS_URL, port=config.REDIS_PORT ,decode_responses=True, username="default", password=config.REDIS_PASSWORD)

class ReplyMetadata(BaseModel):
    label: str = Field(..., description="The UI label, e.g., 'Agree', or 'Custom'")
    # Enforce specific values matching your frontend types
    sentiment: Literal["positive", "negative", "neutral"] 
    is_custom: bool = Field(default=False, description="True if the user typed manually")

class ReplyRequest(BaseModel):
    chat_id: int
    text: List[str]
    card_id: str
    meta: ReplyMetadata

class AddCalendarEventRequest(BaseModel):
    title: str
    datetime: Optional[str]
    time: Optional[str]
    event_type: str


@event_router.post("/reply")
async def send_reply(req: ReplyRequest):
    # 1. Construct the Command Payload
    print(f'Received: {req}')
    command = {
        "action": "reply",
        "chat_id": req.chat_id,
        "text": req.text,
    }

    raw_json = await r.hget("dashboard:items", req.card_id)
    
    if raw_json:
        card_data = json.loads(raw_json)
        detected_sentiment = "custom"
        
        history_context = card_data.get("raw_history_log", "")
        
        log_training_data(
            history=history_context, 
            chosen_reply=req.text,
            metadata=req.meta.model_dump()
        )
    
    # 2. Publish to Redis (The Userbot hears this instantly)
    await r.publish("userbot:commands", json.dumps(command))
    
    # 3. Cleanup: Remove the card from the Dashboard since we handled it
    await r.hdel("dashboard:items", req.card_id)

    await r.hdel("dashboard:active_chats", req.card_id)
    
    return {"status": "sent", "text": req.text}

@event_router.post("/add_event")
async def add_event(req: AddCalendarEventRequest):
    # 1. Construct the Command Payload
    command = {
        "action": "reply",
        "title": req.title,
        "datetime": req.datetime,
        "duration": req.duration,
        "event_type": req.event_type
    }
    
    # 2. Publish to Redis (The Userbot hears this instantly)
    await r.publish("userbot:commands", json.dumps(command))
    
    # 3. Cleanup: Remove the card from the Dashboard since we handled it
    await r.hdel("dashboard:items", req.card_id)
    
    return {"status": "sent", "text": req.title}

@event_router.get("/notifications")
async def get_notifications():
    # HGETALL returns a dict: {'uuid1': 'json1', 'uuid2': 'json2'}
    all_items = await r.hgetall("dashboard:items")
    
    # Convert to a clean list of objects
    parsed_list = [json.loads(val) for val in all_items.values()]
    
    # Sort by timestamp (newest first)
    parsed_list.sort(key=lambda x: x['timestamp'], reverse=True)
    return parsed_list

# 2. LIVE STREAM: Listen for NEW updates
@event_router.get("/stream")
async def stream_events(request: Request):
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
        except asyncio.CancelledError:
            await pubsub.unsubscribe("dashboard:events")

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# 3. ACTION TAKEN: Delete the item
@event_router.delete("/notifications/{card_id}")
async def delete_notification(card_id: str):
    raw_json = await r.hget("dashboard:items", card_id)
    
    if raw_json:
        data = json.loads(raw_json)
        chat_id = data.get('chat_id')
        
        # 2. Remove from Index
        if chat_id:
            await r.hdel("dashboard:active_chats", str(chat_id))

    # 3. Remove from Main Storage
    deleted_count = await r.hdel("dashboard:items", card_id)
    return {"deleted": deleted_count > 0}

