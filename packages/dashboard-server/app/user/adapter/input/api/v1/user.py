import os, json, asyncio
from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, FastAPI, Request
from fastapi.responses import StreamingResponse
import redis.asyncio as redis
from app.container import Container
from app.user.adapter.input.api.v1.request import CreateUserRequest, LoginRequest
from app.user.adapter.input.api.v1.response import LoginResponse
from app.user.application.dto import CreateUserResponseDTO, GetUserListResponseDTO
from app.user.domain.command import CreateUserCommand
from app.user.domain.usecase.user import UserUseCase
from core.fastapi.dependencies import IsAdmin, PermissionDependency

load_dotenv()

user_router = APIRouter()

REDIS_URL = os.getenv('REDIS_URL')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
r = redis.Redis(host=REDIS_URL, port=REDIS_PORT ,decode_responses=True, username="default", password=REDIS_PASSWORD)

class ReplyRequest(BaseModel):
    chat_id: int
    text: List[str]
    card_id: str

class AddCalendarEventRequest(BaseModel):
    title: str
    datetime: Optional[str]
    time: Optional[str]
    event_type: str


@user_router.post("/reply")
async def send_reply(req: ReplyRequest):
    # 1. Construct the Command Payload
    command = {
        "action": "reply",
        "chat_id": req.chat_id,
        "text": req.text
    }
    
    # 2. Publish to Redis (The Userbot hears this instantly)
    await r.publish("userbot:commands", json.dumps(command))
    
    # 3. Cleanup: Remove the card from the Dashboard since we handled it
    await r.hdel("dashboard:items", req.card_id)
    
    return {"status": "sent", "text": req.text}

@user_router.post("/add_event")
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

@user_router.get("/notifications")
async def get_notifications():
    # HGETALL returns a dict: {'uuid1': 'json1', 'uuid2': 'json2'}
    all_items = await r.hgetall("dashboard:items")
    
    # Convert to a clean list of objects
    parsed_list = [json.loads(val) for val in all_items.values()]
    
    # Sort by timestamp (newest first)
    parsed_list.sort(key=lambda x: x['timestamp'], reverse=True)
    return parsed_list

# 2. LIVE STREAM: Listen for NEW updates
@user_router.get("/stream")
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
@user_router.delete("/notifications/{card_id}")
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

# @user_router.get(
#     "",
#     response_model=list[GetUserListResponseDTO],
#     dependencies=[Depends(PermissionDependency([IsAdmin]))],
# )
# @inject
# async def get_user_list(
#     limit: int = Query(10, description="Limit"),
#     prev: int = Query(None, description="Prev ID"),
#     usecase: UserUseCase = Depends(Provide[Container.user_service]),
# ):
#     return await usecase.get_user_list(limit=limit, prev=prev)


# @user_router.post(
#     "",
#     response_model=CreateUserResponseDTO,
# )
# @inject
# async def create_user(
#     request: CreateUserRequest,
#     usecase: UserUseCase = Depends(Provide[Container.user_service]),
# ):
#     command = CreateUserCommand(**request.model_dump())
#     await usecase.create_user(command=command)
#     return {"email": request.email, "nickname": request.nickname}


# @user_router.post(
#     "/login",
#     response_model=LoginResponse,
# )
# @inject
# async def login(
#     request: LoginRequest,
#     usecase: UserUseCase = Depends(Provide[Container.user_service]),
# ):
#     token = await usecase.login(email=request.email, password=request.password)
#     return {"token": token.token, "refresh_token": token.refresh_token}
