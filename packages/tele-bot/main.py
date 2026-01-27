import asyncio, os, json, time, random
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Literal, List
from pydantic import BaseModel, Field
import redis.asyncio as redis
import uuid
from telethon import TelegramClient, events
from google import genai
import EventKit
from Foundation import NSDate, NSTimeZone
from zoneinfo import ZoneInfo

load_dotenv(".env")

GEMINI_MODEL = "gemini-3-pro-preview"
MY_REPLY_STYLE = """
STYLE GUIDE:
- Use lowercase mostly.
- Use 'u' instead of 'you', 'r' instead of 'are'.
- Use Singaporean slang like 'can', 'kennot', 'sien', 'shiet', 'cmi', 'wadaheck' where appropriate.
- **USE EMOJIS:** Use 👍, 😂, 😭, 💀 to convey tone.
- Don't sign off with a name.
- Keep it short.

FEW-SHOT EXAMPLES:

Input: "Hey are you free for dinner tonight?"
Reply Option (Accept): ['can','what time you prefer','I usually free from 6pm onwards']
Reply Option (Decline): ["cannot leh"," got stuff to do."]
Reply Option (Reschedule): ["tonight cannot", "tmr?"]

Input: "Did you finish the assignment?"
Reply Option (Confirm): ["done le"]
Reply Option (Deny): ["shiet","not yet leh","💀","i feel like im done"]

Input: "check out this reels ahhaha"
Reply Option (Ack): ["wadaheck","wat is going on 😂"]

Input: "The meeting is at 2pm."
Reply Option (Ack): ["👍","noted"]
"""

class CalendarEvent(BaseModel):
    title: str = Field(description="The title of the event")
    datetime: Optional[str] = Field(description="event date and time in UTC format")
    duration: Optional[int] = Field(description="Event duration in minutes")
    event_type: Literal['Work','Event','Misc','Due date','Meeting','Trip'] = Field(description="The category of the event")

class ReplyOption(BaseModel):
    label: str = Field(description="Short Header for the button. E.g., 'Accept', 'Decline', 'Ask Time'")
    text: List[str] = Field(description="A list of 1-3 short strings to be sent consecutively. E.g. ['can', 'what time?']")
    sentiment: Literal['positive', 'negative', 'neutral'] = Field(description="Helps the UI color-code the button (Green/Red/Gray)")

class DashboardCard(BaseModel):
    sender: str
    summary: str = Field(description="A concise 1-sentence summary of the intent. Exclude the sender name if there is no third person in the conversation. Include location and time if possible. Example: 'Asked you if you are going school tomorrow.', 'Said your personal project sucks and won't be useful in the future.'")
    urgency: Literal['low', 'medium', 'high']
    suggested_action: Literal['ignore', 'reply', 'calendar_event']

    reply_options: List[ReplyOption] = Field(default_factory=list, description="Generate 2-3 distinct reply choices if action is 'reply'.")
    auto_reply_allowed: bool = Field(description="Set to True ONLY if the incoming message does not require me to make decision. Example: 'yo check this out!','I am arriving, almost there.', 'nice'")
    calendar_details: Optional[CalendarEvent] = Field(description="Extracted if action is calendar_event")

# --- CONFIGURATION ---
TELE_API_ID = os.getenv('TELEGRAM_API_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
TELE_API_HASH = os.getenv('TELEGRAM_API_HASH')
REDIS_URL = os.getenv('REDIS_URL')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# --- SETUP ---

# 2. Setup Redis
redis_client = redis.Redis(host=REDIS_URL, port=REDIS_PORT ,decode_responses=True, username="default", password=REDIS_PASSWORD)

# 2. Setup Gemini (JSON Mode)
google_client = genai.Client(api_key=GEMINI_API_KEY)

# 3. Setup Telegram
tele_client = TelegramClient('anon_gemini', TELE_API_ID, TELE_API_HASH)

# In-memory map to handle the "Debounce" timers
pending_tasks = {}

async def command_listener(client, r):
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

                    print(f"✅ Sent human-like reply: {reply_text_list}")

                elif action == "calendar":
                    title = data.get("title")
                    date_time = data.get("datetime")
                    duration = data.get("duration")
                    event_type = data.get("event_type")
                    add_event_native(title=title, start_dt=date_time, duration_minutes=duration, calendar_type=event_type, alert_minutes_before=30)

    except Exception as e:
        print(f"❌ Error in command listener: {e}")

def prompt_llm(full_conversation: str) -> DashboardCard:
    prompt = f"""
      You are my personal assistant. Analyze this incoming conversation stream and draft replies that sound EXACTLY like me.
    
      {MY_REPLY_STYLE}

      Conversation:
      {full_conversation}

      TASK:
      Analyze the conversation above.
      Extract the summary and urgency.
      If a reply is needed, generate 3 options (Positive, Negative, Neutral) using the STYLE GUIDE and EXAMPLES provided above.

      CRITERIA FOR AUTO-REPLY:
      - TRUE: Message is "I'm here", "Done", "On my way", "Okay".
      - TRUE: Sentiment is purely informational.
      - FALSE: Message involves money, feelings, questions, or emergencies.
      - FALSE: You are unsure.
      """

    try:
        # 3. Call Gemini
        response = google_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": DashboardCard.model_json_schema(),
            },
        )
        card_object: DashboardCard = DashboardCard.model_validate_json(response.text)
        return card_object

    except Exception as e:
        raise
        
async def process_batch(chat_id, sender_name):
    history_objs = await tele_client.get_messages(chat_id, limit=20)
    
    if not history_objs:
        print("🛑 No history object found in telegram client.")
        return

    latest_msg = history_objs[0]
    
    if latest_msg.out:
        print(f"🛑 Skipping {chat_id}: Last message was sent by me.")
        return

    sender_name = "Unknown"
    for m in history_objs:
        if not m.out:
            sender = await m.get_sender()
            sender_name = sender.first_name
            break

    print(f"⚡ Processing batch for {sender_name}...")

    lines = []
    for m in reversed(history_objs):
        if m.text:
            name = "Me" if m.out else sender_name
            lines.append(f"{name}: {m.text}")
            
    full_conversation = "\n".join(lines)
    
    try:
        card_object: DashboardCard = prompt_llm(full_conversation=full_conversation)

        if card_object.auto_reply_allowed and card_object.urgency != 'high':
            print(f"🚀 Auto-Replying to {chat_id}...")
            
            best_reply = card_object.reply_options[0].text
            
            command = {
                "action": "reply",
                "chat_id": chat_id,
                "text": best_reply
            }
            
            await redis_client.publish("userbot:commands", json.dumps(command))
            
            return

        card_dict = card_object.model_dump()

        card_id = str(uuid.uuid4())
        card_dict['id'] = card_id 
        card_dict['chat_id'] = chat_id
        card_dict['timestamp'] = datetime.now().isoformat()

        json_payload = json.dumps(card_dict)

        await redis_client.hset("dashboard:items", card_id, json_payload)
    
        await redis_client.publish("dashboard:events", json_payload)
        print(f"✅ Queued summary for {sender_name}")


    except Exception as e:
        print(f"❌ Error in Gemini/Redis: {e}")

@tele_client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return 

    chat_id = event.chat_id
    sender = await event.get_sender()
    sender_name = sender.first_name or "Unknown"
    
    if chat_id in pending_tasks:
        pending_tasks[chat_id].cancel()
    
    task = asyncio.create_task(wait_and_trigger(chat_id, sender_name))
    pending_tasks[chat_id] = task

async def wait_and_trigger(chat_id, sender_name):
    await asyncio.sleep(45)
    await process_batch(chat_id, sender_name)
    del pending_tasks[chat_id]

def add_event_native(title, start_dt, duration_minutes, calendar_type:str = None, source_name:str = 'iCloud', alert_minutes_before:str = None):
    store = EventKit.EKEventStore.alloc().init()
    
    # Request Access (This usually fails in simple scripts without an app bundle info.plist)
    # Ideally, run this in an environment that already has permissions.
    
    permission_determined = False

    def request_callback(granted, error):
        nonlocal permission_determined
        permission_determined = True
        if granted:
            print("\n✅ SUCCESS: Permission Granted! You can now run your main script.")
        else:
            print("\n❌ DENIED: You clicked 'Don't Allow'. You must fix this in System Settings.")
    
    status = EventKit.EKEventStore.authorizationStatusForEntityType_(EventKit.EKEntityTypeEvent)
    
    if status == 0: # Not Determined
        print("Status: Not Determined. Attempting to trigger popup...")
        
        # New macOS (Sonoma/Sequoia) API vs Old API
        if hasattr(store, "requestFullAccessToEventsWithCompletion_"):
            store.requestFullAccessToEventsWithCompletion_(request_callback)
        else:
            store.requestAccessToEntityType_completion_(EventKit.EKEntityTypeEvent, request_callback)

        # Wait up to 30 seconds for interaction
        counter = 0
        while not permission_determined and counter < 60:
            time.sleep(0.5)
            counter += 1
            
    elif status == 1: # Restricted
        print("Status: Restricted (Parental controls or MDM profile blocking access).")
        return
    elif status == 2: # Denied
        print("Status: Denied. You previously clicked 'Don't Allow'. Run 'tccutil reset Calendar' in terminal.")
        return
    elif status == 3: # Authorized
        print("Status: Authorized. You already have access!")


    # Note: Modern macOS requires explicit permission handling here, 
    # which can be complex for a standalone script.

    event = EventKit.EKEvent.eventWithEventStore_(store)
    event.setTitle_(title)
    event.setLocation_("Singapore")

    if calendar_type:
        # Get all available calendars for events
        all_calendars = store.calendarsForEntityType_(EventKit.EKEntityTypeEvent)
        target_cal = None

        # Search for a match (case-insensitive)
        for cal in all_calendars:
            # Get the names of the Calendar and its Source (Account)
            c_name = cal.title()
            s_name = cal.source().title()
            
            # Check for match (case-insensitive)
            if c_name.lower() == calendar_type.lower() and s_name.lower() == source_name.lower():
                target_cal = cal
                break
        
        if target_cal:
            print(f"📅 Using calendar: {target_cal.title()}")
            event.setCalendar_(target_cal)
        else:
            print(f"⚠️ Warning: Calendar '{calendar_type}' not found. Using default.")
            event.setCalendar_(store.defaultCalendarForNewEvents())
    else:
        print(f"📅 Using default calendar")
        event.setCalendar_(store.defaultCalendarForNewEvents())
    
    if alert_minutes_before is not None:
        offset_seconds = -1 * (alert_minutes_before * 60)
        alarm = EventKit.EKAlarm.alarmWithRelativeOffset_(offset_seconds)
        event.addAlarm_(alarm)
        print(f"🔔 Alert set for {alert_minutes_before} minutes before.")

    if start_dt.tzinfo is None:
        sgt = ZoneInfo("Asia/Singapore")
        start_dt = start_dt.replace(tzinfo=sgt)
        
    timestamp = start_dt.timestamp()
    
    # Create NSDate (Absolute time)
    ns_start = NSDate.dateWithTimeIntervalSince1970_(timestamp)
    ns_end = NSDate.dateWithTimeIntervalSince1970_(timestamp + (duration_minutes * 60))
    
    event.setStartDate_(ns_start)
    event.setEndDate_(ns_end)
    
    # Explicitly set the event metadata to Singapore Time
    sg_tz = NSTimeZone.timeZoneWithName_("Asia/Singapore")
    event.setTimeZone_(sg_tz)
    
    # 5. Save the Event
    result, error = store.saveEvent_span_commit_error_(event, 0, True, None)

    if result:
        print(f"✅ Success: '{title}' added for {start_dt.strftime('%d %b %H:%M')} SGT")
    else:
        print(f"❌ Error saving event: {error}")

async def main():
    print("🚀 Userbot Started...")
    await tele_client.start()
    
    asyncio.create_task(command_listener(tele_client, redis_client))
    await tele_client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())