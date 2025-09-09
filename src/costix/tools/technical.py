


from typing import Annotated
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


class TechnicalDataPoint(BaseModel):
    '''
    The data point that should be added to the technical requirements
    '''
    group:str=Field(...,description='The title of the group')
    component:str=Field(...,description='The name of the component') 
    resource_type_or_service:str=Field(...,description='The type of resource or service')
    recommended_sizing_or_type:str=Field(...,description='The recommended sizing or type')
    quantity_or_notes:str=Field(...,description='The quantity or notes')

def add_to_technical_requirements(
        tool_call_id: Annotated[str, InjectedToolCallId],
        data_point:TechnicalDataPoint,
        technical_requirements: Annotated[list[dict], InjectedState('technical_requirements')]
    ):

    updated_technical_requirements=None
    
    response_tool_message=''
    thought=None
    for item in technical_requirements:
        if item['group']==data_point.group and item['component']==data_point.component:
            item['resource_type_or_service']=data_point.resource_type_or_service
            item['recommended_sizing_or_type']=data_point.recommended_sizing_or_type
            item['quantity_or_notes']=data_point.quantity_or_notes
            updated_technical_requirements=technical_requirements
            response_tool_message=f"Updated existing data point with group {data_point.group} and component {data_point.component}"
            thought=f"Updating Technical Requirements for {data_point.component}"
            break
    if not updated_technical_requirements:
        updated_technical_requirements=data_point.model_dump()
        response_tool_message=f"Added data point with group {data_point.group} and component {data_point.component}"
        thought=f"Updating Technical Requirements for {data_point.component}"
    tool_message=ToolMessage(content=response_tool_message,tool_call_id=tool_call_id)
    return Command(update={'technical_requirements':updated_technical_requirements,'messages':[tool_message],'thoughts':thought})

add_to_technical_requirements_tool=StructuredTool.from_function(
    func=add_to_technical_requirements,
    name='add_to_technical_requirements',
    description='''
    used to add or update a data point in the technical requirements
    ''',
)


def remove_from_technical_requirements(
        group:str,
        component:str,
        tool_call_id: Annotated[str, InjectedToolCallId],
        technical_requirements: Annotated[list[dict], InjectedState('technical_requirements')]
    ):

    if not technical_requirements:
        return "No technical requirements to remove."

    datapoint_deleted=False
    for datapoint in technical_requirements:
        if datapoint['group']==group and datapoint['component']==component:
            technical_requirements.remove(datapoint)
            datapoint_deleted=True
            break

    if not datapoint_deleted:
        return f"Data point with group {group} and component {component} not found in technical requirements"
    else:
        tool_response_message=f"Removed data point with group {group} and component {component}"
        tool_message=ToolMessage(content=tool_response_message,tool_call_id=tool_call_id)
        thought=f"Removing {component} from technical requirements"
        return Command(update={'technical_requirements':technical_requirements,'messages':[tool_message],'thoughts':thought})


remove_from_technical_requirements_tool=StructuredTool.from_function(
    func=remove_from_technical_requirements,
    name='remove_from_technical_requirements',
    description='''
    used to remove a data point from the technical requirements
    Args:
        group: The group of the data point
        component: The component of the data point 
    ''',
)