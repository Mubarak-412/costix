



from typing import Annotated, List
from pydantic import BaseModel,Field
from langchain.tools import StructuredTool
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command

	# <th><b>Component</b></th>
	# 					<th><b>esource Type / Service</b></th>
	# 					<th><b>Recommended Sizing/Type</b></th>
	# 					<th><b>Quantity / Notes</b></th>


class EstimateDataPoint(BaseModel):
    '''
    The data point in the estimate that represents a cost item
    '''
    group:str=Field(...,description='The title of the group')
    component:str=Field(...,description='The name of the component') 
    subtitle:str=Field(...,description='The subtitle of the component')
    rate:str=Field(...,description='The cost rate or pricing information for this component')
    monthly_estimate:float=Field(...,description='The monthly estimate for this component')
    notes:List[str]=Field(...,description='notes for the compnent')
    
    
def add_to_estimate(
        tool_call_id: Annotated[str, InjectedToolCallId],
        data_point:EstimateDataPoint,
        estimate: Annotated[list[dict], InjectedState('estimate')]
    ):

    updated_estimate=None
    
    response_tool_message=''
    thought_text=None
    for item in estimate:
        if item['group']==data_point.group and item['component']==data_point.component:
            item['subtitle']=data_point.subtitle
            item['rate']=data_point.rate
            item['monthly_estimate']=data_point.monthly_estimate
            item['notes']=data_point.notes
            updated_estimate=estimate
            response_tool_message=f"Updated existing data point with group {data_point.group} and component {data_point.component}"
            thought_text=f"Updating Estimate for {data_point.component}"
            break
    if not updated_estimate:
        updated_estimate=data_point.model_dump()
        response_tool_message=f"Added data point with group {data_point.group} and component {data_point.component}"
        thought_text=f"Updating Estimate for {data_point.component}"
    tool_message=ToolMessage(content=response_tool_message,tool_call_id=tool_call_id)
    thought={'type':'text','text':thought_text}
    return Command(update={'estimate':updated_estimate,'messages':[tool_message],'thoughts':thought})

add_to_estimate_tool=StructuredTool.from_function(
    func=add_to_estimate,
    name='add_to_estimate',
    description='''
    used to add or update a data point in the estimate
    ''',
)


def remove_from_estimate(
        group:str,
        component:str,
        tool_call_id: Annotated[str, InjectedToolCallId],
        estimate: Annotated[list[dict], InjectedState('estimate')]
    ):

    if not estimate:
        return "No estimate to remove."

    datapoint_deleted=False
    for datapoint in estimate:
        if datapoint['group']==group and datapoint['component']==component:
            estimate.remove(datapoint)
            datapoint_deleted=True
            break

    if not datapoint_deleted:
        return f"Data point with group {group} and component {component} not found in technical requirements"
    else:
        tool_response_message=f"Removed data point with group {group} and component {component}"
        tool_message=ToolMessage(content=tool_response_message,tool_call_id=tool_call_id)
        thought={'type':'text','text':f"Removing {component} from estimate"}
        return Command(update={'estimate':estimate,'messages':[tool_message],'thoughts':thought})


remove_from_estimate_tool=StructuredTool.from_function(
    func=remove_from_estimate,
    name='remove_from_estimate',
    description='''
    used to remove a data point from the estimate
    Args:
        group: The group of the data point
        component: The component of the data point 
    ''',
)