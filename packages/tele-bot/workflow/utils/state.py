from typing import List, Annotated, Optional
from typing_extensions import TypedDict
from telethon.types import Message
from langgraph.graph.message import add_messages
from schemas.reply import DashboardCard

class State(TypedDict):
    chat_id: str
    chat_history: List[Message]
    messages: Annotated[list, add_messages]
    dashboard_card: DashboardCard
