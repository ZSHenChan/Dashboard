from typing import List, Literal
from langgraph.prebuilt import ToolNode
from langgraph.graph import END
from langchain.tools import tool, ToolRuntime
from .context import UserContext
from workflow.utils.state import State
from lib.mem0ai_client import memoai_client
from lib.tele_client import tele_client
from telethon.types import Message
from utils.aggregate_chat import aggregate_chat_history

def should_continue(state: State) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"
    
    return END

def search_memories(user_id: str, query: str):
    filters = {
      "OR":[
          {
            "user_id": user_id
          }
      ]
    }
    search_memory_response = memoai_client.search(query=query, filters=filters, version="v2", output_format="v1.1")
    return search_memory_response['results']

@tool
def search_memory(query: str, runtime: ToolRuntime[UserContext]) -> str:
    """Search for memories regarding the user (not Zi Shen).

    Args:
        query: Search key words to look for, an example will be 'party at Bangkok'
    """
    user_id = runtime.context.user_id
    memories = search_memories(user_id, query)
    context = "\\n".join(m["memory"] for m in memories)

    return context

@tool
def search_calendar(start_date: str, end_date: str) -> str:
    """Search for calendar events within a time window.

    Args:
        start_date: Start date of window (inclusive), format: dd/mm/yyyy
        end_date: End date of window (inclusive), format" dd/mm/yyyy
    """
    return f"Event: Dentist Appointment | Start: 10:00 AM {start_date} | End: 11:30 AM {end_date}"

@tool
async def search_chat_context(limit: int, runtime: ToolRuntime[UserContext]) -> str:
    """Search for more chat history context regarding the conversation.

    Args:
        limit: the number of chat history bubble count
    """
    history_objs: List[Message] = await tele_client.get_messages(runtime.context.chat_id, limit=limit)
    lines: List[str] = await aggregate_chat_history(history_objs)

    return "\n".join(lines)

search_chat_toolnode = ToolNode([search_chat_context])
