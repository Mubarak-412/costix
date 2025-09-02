from typing import Annotated
from pydantic import BaseModel,Field
from langchain.tools import StructuredTool
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command



class SolutionDataPoint(BaseModel):
    '''
    The data point that should be added to the solution
    '''
    group:str=Field(...,description='The title of the group')
    title:str=Field(...,description='The key of the data point')
    value:str=Field(...,description='The value of the data point')

def add_to_solution(
        tool_call_id: Annotated[str, InjectedToolCallId],
        data_point:SolutionDataPoint,
        solution: Annotated[list[dict], InjectedState('solution')]
    ):

    updated_solution=None
    
    response_tool_message=''
    thought=None
    for item in solution:
        if item['group']==data_point.group and item['title']==data_point.title:
            item['value']=data_point.value
            updated_solution=solution
            response_tool_message=f"Updated existing data point with group {data_point.group} and title {data_point.title}"
            thought=f"Updating Solution for {data_point.title}"
            break
    if not updated_solution:
        updated_solution=data_point.model_dump()
        response_tool_message=f"Added data point with group {data_point.group} and title {data_point.title}"
        thought=f"Updating Solution for {data_point.title}"
    tool_message=ToolMessage(content=response_tool_message,tool_call_id=tool_call_id)
    return Command(update={'solution':updated_solution,'messages':[tool_message],'thoughts':thought})

add_to_solution_tool=StructuredTool.from_function(
    func=add_to_solution,
    name='add_to_solution',
    description='''
    used to add or update a data point to the solution
    ''',
)


def remove_from_solution(
        group:str,
        title:str,
        tool_call_id: Annotated[str, InjectedToolCallId],
        solution: Annotated[list[dict], InjectedState('solution')]
    ):

    datapoint_deleted=False
    for datapoint in solution:
        if datapoint['group']==group and datapoint['title']==title:
            solution.remove(datapoint)
            datapoint_deleted=True
            break

    if not datapoint_deleted:
        return f"Data point with group {group} and title {title} not found in solution"
    else:
        tool_response_message=f"Removed data point with group {group} and title {title}"
        tool_message=ToolMessage(content=tool_response_message,tool_call_id=tool_call_id)
        thought=f"Removing {title} from solution"
        return Command(update={'solution':solution,'messages':[tool_message],'thoughts':thought})


remove_from_solution_tool=StructuredTool.from_function(
    func=remove_from_solution,
    name='remove_from_solution',
    description='''
    used to remove a data point from the solution
    Args:
        group: The group of the data point
        title: The title of the data point
    ''',
)