import asyncio
import json
import random
import uuid
from typing import List
from schemas.calendar import CalendarEvent
from lib.redis_client import redis_client

class CommandListener():
    async def listen_command(self, client, r):
        print("🎧 Userbot listening for dashboard commands...")
        pubsub = r.pubsub()
        await pubsub.subscribe("userbot:commands")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    
                    # EXTRACT COMMAND DETAILS
                    action = data.get("action")
                    chat_id = data.get("chat_id")
                    
                    print(f"⚡ Received command: {action} for chat {chat_id}")

                    if action == "reply":
                        reply_text_list: List[str] = data.get("text")
                        for txt in reply_text_list:
                            async with client.action(chat_id, 'typing'):
                                
                                base_time = len(txt) * 0.1
                                typing_delay = min(max(base_time, 1.0), 5.0)
                                
                                fuzzy_delay = typing_delay * random.uniform(0.8, 1.3)
                                
                                await asyncio.sleep(fuzzy_delay)
                                
                                await client.send_message(chat_id, txt)
                        
                            await asyncio.sleep(random.uniform(0.3, 0.8))

                        print(f"✅ Sent {len(reply_text_list)} chat bubbles")

                    elif action == "calendar":
                        calendar_event = CalendarEvent()
                        calendar_event.title = data.get("title")
                        calendar_event.datetime = data.get("datetime")
                        calendar_event.duration = data.get("duration")
                        calendar_event.event_type = data.get("event_type")
                        await self.add_calendar_event(calendar_event)

        except Exception as e:
            print(f"❌ Error in command listener: {e}")

    async def add_calendar_event(self, event: CalendarEvent) -> None:
        event_id = str(uuid.uuid4())
        json_payload = json.dumps(event)
        await redis_client.hset("calendar:items", event_id, json_payload)
        await redis_client.publish("calendar:events", json_payload)

command_listener = CommandListener()
