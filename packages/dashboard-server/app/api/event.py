import os, json, asyncio
import logging
from contextlib import contextmanager
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from core.config import config
from fastapi import APIRouter, Depends, Query, FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi import BackgroundTasks
from .logger import log_training_data
from core.redis_db import r
from core.fastapi.logging_config import SensitiveDataFilter

event_router = APIRouter(prefix="/event", tags=["Event"])

class ReplyMetadata(BaseModel):
    label: str = Field(..., description="The UI label, e.g., 'Agree', or 'Custom'")
    sentiment: Literal["positive", "negative", "neutral"] 
    is_custom: bool = Field(default=False, description="True if the user typed manually")

class ReplyRequest(BaseModel):
    chat_id: int
    text: List[str]
    card_id: str
    meta: ReplyMetadata

async def _send_log_task(log_path: str):
    """
    Reads the completed log file and processes/sends it.
    """
    print(f"Background Task: Processing log file at {log_path}...")

@contextmanager
def session_logger_with_task(background_tasks: BackgroundTasks, log_path: str):
    """
    Context manager to handle session-specific logging setup/teardown.
    NOW WITH SENSITIVE DATA FILTERING!
    """
    # 1. Setup the File Handler (Dynamic File)
    handler = logging.FileHandler(log_path)
    sess_formatter = logging.Formatter(config.SESS_LOG_FORMAT)
    handler.setFormatter(sess_formatter)
    handler.setLevel(logging.DEBUG)
    
    # --- UPGRADE: Add the Sensitive Filter to this specific handler ---
    # This ensures the uploaded file has secrets masked too.
    handler.addFilter(SensitiveDataFilter()) 

    # 2. Get the Logger
    sess_logger = logging.getLogger(config.SESSION_LOGGER_NAME)
    sess_logger.setLevel(logging.DEBUG)
    sess_logger.addHandler(handler)
    
    # 3. Stop Propagation
    # Crucial: This stops these logs from leaking into your main 'my_customer_logger'
    # or the console. It keeps this session strictly private to this file.
    sess_logger.propagate = False 

    try:
        yield sess_logger
    finally:
        # --- TEARDOWN ---
        sess_logger.removeHandler(handler)
        handler.close() # Close file so it can be read by the task below
        
        # 4. Queue the background task
        background_tasks.add_task(_send_log_task, log_path)

@event_router.post("/reply")
async def send_reply(req: ReplyRequest, background_tasks: BackgroundTasks):
    # 1. Construct the Command Payload
    with session_logger_with_task(background_tasks, config.SESSION_LOG_FILE_PATH) as logger:
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

    with session_logger_with_task(background_tasks, config.SESSION_LOG_FILE_PATH) as logger:
        # HGETALL returns a dict: {'uuid1': 'json1', 'uuid2': 'json2'}
        all_items = await r.hgetall("dashboard:items")
        
        # Convert to a clean list of objects
        parsed_list = [json.loads(val) for val in all_items.values()]
        
        # Sort by timestamp (newest first)
        parsed_list.sort(key=lambda x: x['timestamp'], reverse=True)

        logger.info(f"Retrieved {len(parsed_list)} notifications.")

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
                    print('Sent stream')
        except asyncio.CancelledError:
            await pubsub.unsubscribe("dashboard:events")

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# 3. ACTION TAKEN: Delete the item
@event_router.delete("/notifications/{card_id}")
async def delete_notification(card_id: str):

    with session_logger_with_task(background_tasks, config.SESSION_LOG_FILE_PATH) as logger:
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

