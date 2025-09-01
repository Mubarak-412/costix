from typing import TypeVar, Union, Callable
from enum import StrEnum
from typing import TypedDict,NotRequired,Annotated,Sequence
from pydantic import BaseModel,Field
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

CostixPhaseToNodeMap={
    CostixPhase.INFORMATION_GATHERING:CostixNodes.INFO_AGENT,
    CostixPhase.SOLUTION_GENERATION:CostixNodes.SOLUTION_AGENT,
}



T = TypeVar("T")

def make_add_or_update_reducer(type_: type[T]) -> Callable[[list[T], Union[list[T], T]], list[T]]:
    def add_or_update_reducer(prev_data: list[T], new_data: Union[list[T], T]) -> list[T]:
        if isinstance(new_data, list):
            return new_data
        elif isinstance(new_data, type_):
            prev_data.append(new_data)
            return prev_data
        else:
            print(f"Expected {type_.__name__}, got {type(new_data).__name__}")
            return prev_data
            # raise (f"Expected {type_.__name__}, got {type(new_data).__name__}")
    return add_or_update_reducer

def thoughts_reducer(prev_thoughts,new_thoughts:list[str]|str):
    '''
    Reducer function for the thoughts field in the CostixState.
        if new value is a single str then append it to the list
        if new value is a list then replace the old list with the new one
    '''
    if isinstance(new_thoughts,str):
        prev_thoughts.append(new_thoughts)
        return prev_thoughts
    elif isinstance(new_thoughts,list):
        return new_thoughts
    else:
        print('new_thoughts is of unknown type',type(new_thoughts),new_thoughts)
        return prev_thoughts


def replace_reducer(prev,new):
    return new

class CostixState(TypedDict):
    '''
    State schema for the COSTIX estimation process.
    '''
    user_input: str=''                                          # >stores the user input
    messages: Annotated[Sequence[BaseMessage], add_messages]    # >stores the message context
    messages_history: Annotated[Sequence[BaseMessage], add_messages]=[]                   # >stores the message history for the chat(ui)
    current_phase: CostixPhase=CostixPhase.INFORMATION_GATHERING
    thoughts:Annotated[list[str],make_add_or_update_reducer(str)]=[]
    collected_data:Annotated[list[dict],make_add_or_update_reducer(dict)]=[]
    solution:Annotated[list[dict],make_add_or_update_reducer(dict)]=[]
    uploaded_files:list[str]=[]                                 # stores the list of files(names) uploaded by the user




class CostixAgentState(CostixState):
    '''
    state schema for agents that have both agent state and costix state keys
    '''
    remaining_steps: NotRequired[RemainingSteps]   # extra key required by create_react_agent



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
    response:str|None=Field(None,description='a optional Field to respond to any user query ')
    title:str=Field(...,description='The title of the question')
    subtitle:str=Field(...,description='The subtitle of the question')
    type:QuestionTypes=Field(...,description='The type of the question to ask the user')
    options:list[str]=Field([],description='The options for the question')
