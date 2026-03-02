import os, json, asyncio
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends
import redis.asyncio as redis
from app.api.dependencies import get_redis_client

calendar_router = APIRouter(prefix="/calendar", tags=["Calendar"])

class AddCalendarEventRequest(BaseModel):
    title: str
    datetime: Optional[str]
    time: Optional[str]
    event_type: str

@calendar_router.post("/add_event")
async def add_event(req: AddCalendarEventRequest, cache: redis.Redis = Depends(get_redis_client)):
    command = {
        "action": "reply",
        "title": req.title,
        "datetime": req.datetime,
        "duration": req.duration,
        "event_type": req.event_type
    }
    
    await cache.publish("userbot:commands", json.dumps(command))
    
    await cache.hdel("dashboard:items", req.card_id)
    
    return {"status": "sent", "text": req.title}
