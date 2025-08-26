import json
from typing import Annotated
from enum import StrEnum
from langchain_core.messages import AIMessage
from pydantic import BaseModel,Field
from langgraph.prebuilt import InjectedState
from langchain_core.tools import StructuredTool
class QuestionTypes(StrEnum):
    '''
    The type of question to ask the user
    '''
    SINGLE_SELECT='single_select'
    MULTI_SELECT='multi_select'
    TEXT='text'

class QuestionSchema(BaseModel):
    '''
    The Question that should be asked to the user
    '''
    title:str=Field(...,description='The title of the question')
    subtitle:str=Field(...,description='The subtitle of the question')
    type:QuestionTypes=Field(...,description='The type of the question to ask the user')
    options:list[str]=Field([],description='The options for the question')



def ask_question(question:QuestionSchema, graph_state: Annotated[dict, InjectedState]):
    graph_state['messages_history']+=[AIMessage(content=json.dumps(question.model_dump()))]
    print(question)
    return 'question displayed successfully'


ask_question_tool=StructuredTool.from_function(
    func=ask_question,
    name='ask_question',
    description='used to present a question to the user, multi select questions are prefered for better user experience',
)