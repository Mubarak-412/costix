import json
from typing import Annotated
from enum import StrEnum
from langchain_core.messages import AIMessage
from pydantic import BaseModel,Field
from langgraph.prebuilt import InjectedState
from langchain_core.tools import StructuredTool
from costix.schemas import QuestionSchema

def ask_question(question:QuestionSchema, graph_state: Annotated[dict, InjectedState]):
    graph_state['messages_history']+=[AIMessage(content=json.dumps(question.model_dump()))]
    print(question)
    return 'question displayed successfully'


ask_question_tool=StructuredTool.from_function(
    func=ask_question,
    name='ask_question',
    description='used to present a question to the user, multi select questions are prefered for better user experience',
)