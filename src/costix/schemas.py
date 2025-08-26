from enum import StrEnum
from typing import TypedDict,NotRequired,Annotated,Sequence
from langchain.chat_models.base import BaseChatModel
from langchain.llms.base import BaseLLM
from langchain_core.messages import BaseMessage


from langgraph.managed import RemainingSteps
from langgraph.graph.message import add_messages
class Model(BaseLLM , BaseChatModel):
    pass

class CostixPhase(StrEnum):
    '''
    Enum representing the different phases of the COSTIX estimation process.
    '''
    INFORMATION_GATHERING='INFORMATION_GATHERING'
    SOLUTION_GENERATION='SOLUTION_GENERATION'
    TECHNICAL='TECHNICAL'
    ESTIMATION='ESTIMATION'


class CostixNodes(StrEnum):
    '''
    Enum representing the different node names in the COSTIX estimation process.
    '''
    INFO_AGENT='info_agent'
    SOLUTION_AGENT='solution_agent'
    TECHNICAL_AGENT='technical_agent'
    ESTIMATION_AGENT='estimation_agent'




class CostixState(TypedDict):
    '''
    State schema for the COSTIX estimation process.
    '''
    user_input: str=''                                          # >stores the user input
    messages: Annotated[Sequence[BaseMessage], add_messages]    # >stores the message context
    messages_history: Annotated[Sequence[BaseMessage], add_messages]                   # >stores the message history for the chat(ui)
    current_phase: CostixPhase=CostixPhase.INFORMATION_GATHERING
    collected_data:list[dict]=[]
    uploaded_files:list[str]=[]                                 # stores the list of files(names) uploaded by the user




class CostixAgentState(CostixState):
    '''
    state schema for agents that have both agent state and costix state keys
    '''
    remaining_steps: NotRequired[RemainingSteps]   # extra key required by create_react_agent



