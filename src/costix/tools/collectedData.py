from typing import Annotated

from langchain_core.tools import StructuredTool
from langgraph.prebuilt import InjectedState
from pydantic import BaseModel,Field

class DataPoint(BaseModel):
    """
    A data point to be collected.
    """
    title:str=Field(...,description="The title of the data point.")
    value:str=Field(...,description="The value of the data point.")
    group:str=Field(...,description="The group of the data point.")

def add_to_collected_data(data: DataPoint, graph_state: Annotated[dict, InjectedState]):
    """
    Add data points to the collected data.
    """

    if "collected_data" not in graph_state:
        graph_state["collected_data"] = []

    for datapoint in graph_state['collected_data']:
        if datapoint['title']==data.title:
            datapoints_copy=graph_state['collected_data'].copy()
            datapoints_copy.remove(datapoint)
            datapoints_copy+=[data.model_dump()]
            graph_state['collected_data']=datapoints_copy
            return f"Updated data point with title {data.title}"
    
    graph_state['collected_data']+=[data.model_dump()]
      
    print(f'Added data point to collected data: {data}')
    return f"Added data point with title {data.title}"


add_to_collected_data_tool = StructuredTool.from_function(
    func=add_to_collected_data,
    name="add_to_collected_data",
    description="Use this tool to add data points to the collected data.",
    )




def remove_from_collected_data(title: str, graph_state: Annotated[dict, InjectedState]):
    """
    Remove data points from the collected data.
    Args:
        title (str): The title of the data point to remove.
    """
    
    if "collected_data" not in graph_state:
        return "No collected data to remove."
    
    data_point_deleted=False

    for data_point in graph_state['collected_data']:
        if data_point['title']==title:
                                                                                            
            graph_state['collected_data']=[                      # graph state need to be reassigned inorder to push changes
                dp for dp in graph_state['collected_data'] if dp['title']!=title
                ] 
            data_point_deleted=True
            break
    if not data_point_deleted:
        print(f'No data point with title {title} found in collected data.')
        return f"No data point with title {title} found in collected data."
    print(f'Removed data point with title {title} from collected data.')
    return "Removed data point successfully"


remove_from_collected_data_tool = StructuredTool.from_function(
    func=remove_from_collected_data,
    name="remove_from_collected_data",
    description="Use this tool to remove data points from the collected data.",
    )