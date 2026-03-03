import json
import uuid
from datetime import datetime
from typing import List
from lib.redis_client import redis_client
from schemas.reply import DashboardCard
from workflow.chain import chain
from workflow.utils.context import UserContext
from telethon.types import Message
from utils.aggregate_chat import aggregate_chat_history

class MainProcessWorker():
    def __init__(self):
        pass
    
    async def process_batch(self, chat_id: str, card_name:str, history_objs: List[Message]):
        latest_msg = history_objs[0]
        lines = await aggregate_chat_history(history_objs)
        
        if latest_msg.out:
            print(f"🛑 Skipping {chat_id}: Last message was sent by me.")
            return

        try:
            existing_card_id = await redis_client.hget("dashboard:active_chats", str(chat_id))
            
            if existing_card_id:
                print(f"🔄 Follow-up detected for {chat_id}. Removing stale card {existing_card_id}...")
                
                await redis_client.hdel("dashboard:items", existing_card_id)
                
                delete_event = json.dumps({"action": "delete", "id": existing_card_id})
                await redis_client.publish("dashboard:events", delete_event)
        
            state = await chain.ainvoke({'chat_id':chat_id,'chat_history':history_objs},context=UserContext(memory_user_id='Lewis',chat_id=chat_id))
            print(state)
            card_object: DashboardCard = state['dashboard_card']

            # if card_object.auto_reply_allowed and card_object.urgency != 'high':
            #     print(f"🚀 Auto-Replying to {chat_id}...")
                
            #     best_reply = card_object.reply_options[0].text
                
            #     command = {
            #         "action": "reply",
            #         "chat_id": chat_id,
            #         "text": best_reply
            #     }
                
            #     await redis_client.publish("userbot:commands", json.dumps(command))
                
            #     return

            card_dict = card_object.model_dump()

            card_id = str(uuid.uuid4())
            card_dict['id'] = card_id
            card_dict['title'] = card_name
            card_dict['chat_id'] = chat_id
            card_dict['timestamp'] = datetime.now().isoformat()
            card_dict['conversation_history'] = lines

            json_payload = json.dumps(card_dict)

            # Store to database
            await redis_client.hset("dashboard:items", card_id, json_payload)

            await redis_client.hset("dashboard:active_chats", str(chat_id), card_id)
            
            await redis_client.publish("dashboard:events", json_payload)
            print(f"✅ Queued summary for {chat_id}")

        except Exception as e:
            print(f"❌ Error in Gemini/Redis: {e}")

main_process_worker = MainProcessWorker()
