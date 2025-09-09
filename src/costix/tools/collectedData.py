from typing import Annotated

from pydantic import BaseModel,Field
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command



class DataPoint(BaseModel):
    """
    A data point to be collected.
    """
    title:str=Field(...,description="The title of the data point.")
    value:str=Field(...,description="The value of the data point.")
    group:str=Field(...,description="The group of the data point.")

def add_to_collected_data(
        data: DataPoint,
        tool_call_id: Annotated[str, InjectedToolCallId], 
        collected_data: Annotated[list[dict], InjectedState('collected_data')]):
    """
    Add data points to the collected data.
    """
    response_tool_message=''
    new_collected_data=None
    thought=None
    if not collected_data:
        collected_data=[]

    for datapoint in collected_data:
        if datapoint['group']==data.group and datapoint['title']==data.title:
            datapoint['value']=data.value
            response_tool_message=f"Updated data point with title {data.title}"
            new_collected_data=collected_data
            thought=f"Updating Requirements for {data.title}"
            break
    else:
        new_collected_data=data.model_dump()
        response_tool_message=f"Added data point with title {data.title}"
        thought=f"Adding Requirements for {data.title}"
   
    tool_message=ToolMessage(content=response_tool_message,tool_call_id=tool_call_id)
    updates={'collected_data':new_collected_data,'messages':[tool_message],'thoughts':thought}
    return Command(update=updates)
      



add_to_collected_data_tool = StructuredTool.from_function(
    func=add_to_collected_data,
    name="add_to_collected_data",
    description="Use this tool to add data points to the collected data.",
    )




def remove_from_collected_data(
    title: str, 
    tool_call_id: Annotated[str, InjectedToolCallId],
    collected_data: Annotated[list[dict], InjectedState('collected_data')]):
    """
    Remove data points from the collected data.
    Args:
        title (str): The title of the data point to remove.
    """

    
    if not collected_data:
        return "No collected data to remove."
    response_tool_message=''
    data_point_deleted=False

    for data_point in collected_data:
        if data_point['title']==title:

            collected_data.remove(data_point)
            data_point_deleted=True
            break
    if not data_point_deleted:
        response_tool_message=f'No data point with title {title} found in collected data.'
    else:
        response_tool_message=f'Removed data point with title {title} from collected data.'
    print(response_tool_message)
    tool_message=ToolMessage(content=response_tool_message,tool_call_id=tool_call_id)
    return Command(update={'collected_data':collected_data,'messages':[tool_message]})


remove_from_collected_data_tool = StructuredTool.from_function(
    func=remove_from_collected_data,
    name="remove_from_collected_data",
    description="Use this tool to remove data points from the collected data.",
    )