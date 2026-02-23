import asyncio
import json
import random
from typing import List
from bot.calendar_handler import calendar_handler

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
                        title = data.get("title")
                        date_time = data.get("datetime")
                        duration = data.get("duration")
                        event_type = data.get("event_type")
                        calendar_handler.add_event_native(title=title, start_dt=date_time, duration_minutes=duration, calendar_type=event_type, alert_minutes_before=30)

        except Exception as e:
            print(f"❌ Error in command listener: {e}")

command_listener = CommandListener()
