from typing import List

async def aggregate_chat_history(history_objs) -> List[str] :
    lines: List[str] = []

    for m in reversed(history_objs):
        if m.text:
            sender = await m.get_sender()
            sender_name = sender.first_name or "Unknown"
            name = "Me" if m.out else sender_name
            lines.append(f"{name}: {m.text}")

    return lines
