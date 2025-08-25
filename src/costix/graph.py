from langgraph.graph import StateGraph, START, END
from pydantic import TypedDict
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage,BaseMessage
from typing import Literal

class CostixState(TypedDict):
    messages: list[dict]                    # >stores the message context
    messages_history: list[BaseMessage]     # >stores the message history for the chat(ui)
    current_phase: Literal["INFORMATION_GATHERING", "SOLUTION", "TECHNICAL","ESTIMATE"]='INFORMATION_GATHERING'
    collected_data:list[dict]
    uploaded_files:list[str]                # stores the list of files(names) uploaded by the user

    

class CostixGraph:

    def __init__(self):

        self.graph = StateGraph(CostixState)






    def