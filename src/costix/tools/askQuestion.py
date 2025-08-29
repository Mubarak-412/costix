import json
from typing import Annotated
from enum import StrEnum
from langchain_core.messages import AIMessage
from langgraph.graph import END
from pydantic import BaseModel,Field
from costix.schemas import QuestionSchema
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command




def ask_question(
        question:QuestionSchema,
        tool_call_id: Annotated[str, InjectedToolCallId],
        graph_state: Annotated[dict, InjectedState]
    ):
    '''
    used to present a question to the user, multi select questions are prefered for better user experience
    '''

    question_json=question.model_dump_json()
    question_message=AIMessage(question_json)
    tool_message=ToolMessage('Question displayed Sucessfully',tool_call_id=tool_call_id)
    return Command(update={'messages':[tool_message],'messages_history':[question_message]},goto=END)


ask_question_tool=StructuredTool.from_function(
    func=ask_question,
    name='ask_question',
    description='used to present a question to the user, multi select questions are prefered for better user experience',
)