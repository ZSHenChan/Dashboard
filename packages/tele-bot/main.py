import asyncio
from telethon import events
from bot.command_listener import command_listener
from bot.main_process_worker import main_process_worker
from config import settings
from lib.redis_client import redis_client
from lib.tele_client import tele_client

pending_tasks = {}

async def process_batch(chat_id, card_name):
    history_objs = await tele_client.get_messages(chat_id, limit=20)
    await main_process_worker.process_batch(chat_id=chat_id, card_name=card_name, history_objs=history_objs)
    
@tele_client.on(events.NewMessage(incoming=True))
async def handler(event):
    if settings.omit_group_messages:
        if not event.is_private:
            return

    if event.is_channel:
        return

    raw_omitted: set = await redis_client.smembers("userbot:omit")
    omitted_chat_id = {int(chat) for chat in raw_omitted}

    chat_id = event.chat_id
    if chat_id in omitted_chat_id:
        print(f"Skipping muted chat {chat_id}")
        return
    card_name = "Unknown"

    if event.is_group:
        chat_from = event.chat if event.chat else (await event.get_chat()) # telegram MAY not send the chat enity
        card_name = chat_from.title or "Unknown"

    if event.is_private:
        sender = await event.get_sender()
        card_name = sender.first_name or "Unknown"
    
    if chat_id in pending_tasks:
        pending_tasks[chat_id].cancel()
    
    task = asyncio.create_task(wait_and_trigger(chat_id, card_name))
    pending_tasks[chat_id] = task

async def wait_and_trigger(chat_id, card_name):
    await asyncio.sleep(settings.debounce_buffer_sec)
    await process_batch(chat_id, card_name)
    del pending_tasks[chat_id]


async def main():
    print("🚀 Userbot Started...")
    await tele_client.start()
    
    asyncio.create_task(command_listener.listen_command(tele_client, redis_client))
    await tele_client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())