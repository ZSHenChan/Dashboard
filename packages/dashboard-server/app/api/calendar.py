import os, json, asyncio
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter
from core.redis_db import r

calendar_router = APIRouter(prefix="/calendar", tags=["Calendar"])

class AddCalendarEventRequest(BaseModel):
    title: str
    datetime: Optional[str]
    time: Optional[str]
    event_type: str

@calendar_router.post("/add_event")
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
