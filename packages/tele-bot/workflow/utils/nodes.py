from config import settings
from .tools import search_chat_context
from langchain_google_genai import ChatGoogleGenerativeAI
from .state import State
from utils.aggregate_chat import aggregate_chat_history
from lib.mlflow_client import mlflow_client
from langchain_core.messages import SystemMessage, HumanMessage
from schemas.reply import DashboardCard

llm = ChatGoogleGenerativeAI(model=settings.gemini_model, temperature=0.7, api_key=settings.gemini_api_key.get_secret_value())

async def summarize_context(state: State):
    """LLM call to summarize context"""
    chat_history_obj = state['chat_history']
    lines = await aggregate_chat_history(chat_history_obj)

    sys_instruction = mlflow_client.load_prompt_template(settings.ml_flow_sys_summary)
    messages = [
      SystemMessage(content=sys_instruction),
      HumanMessage(content="\n".join(lines))
    ]
    
    tools = [search_chat_context]
    llm_with_tools = llm.bind_tools(tools)

    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

async def generate_replies(state: State):
    """LLM call to generate replies"""
    structured_llm = llm.with_structured_output(DashboardCard)
    
    sys_instruction = mlflow_client.load_prompt(settings.ml_flow_sys_reply)
    sys_reply_style = mlflow_client.load_prompt_template(settings.ml_flow_prompt_style)
    formatted_sys_ins = sys_instruction.format(reply_style=sys_reply_style)

    prompt_template = mlflow_client.load_prompt(settings.ml_flow_prompt_reply)
    formatted_prompt_template = prompt_template.format(summary=state['messages'][-1].content[0]['text'], memory='No memory found')

    messages = [
      SystemMessage(content=formatted_sys_ins),
      HumanMessage(content=formatted_prompt_template)
    ]

    response = await structured_llm.ainvoke(messages)
    return {"dashboard_card": response}




