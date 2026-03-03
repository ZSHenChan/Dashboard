from langgraph.graph import StateGraph, END
from .utils.state import State
from .utils.nodes import summarize_context, generate_replies
from .utils.tools import search_chat_toolnode

workflow = StateGraph(State)

workflow.set_entry_point(summarize_context.__name__)
workflow.add_node(summarize_context.__name__, summarize_context)
workflow.add_node('tools', search_chat_toolnode)
workflow.add_edge('tools', summarize_context.__name__)
workflow.add_node(generate_replies.__name__, generate_replies)
workflow.add_edge(summarize_context.__name__, generate_replies.__name__)
workflow.add_edge(generate_replies.__name__, END)

chain = workflow.compile()
