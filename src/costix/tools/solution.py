from typing import Annotated
from pydantic import BaseModel,Field
from langgraph.prebuilt import InjectedState
from langchain.tools import StructuredTool



class SolutionDataPoint(BaseModel):
    '''
    The data point that should be added to the solution
    '''
    group:str=Field(...,description='The title of the group')
    key:str=Field(...,description='The key of the data point')
    value:str=Field(...,description='The value of the data point')

def add_to_solution(data_point:SolutionDataPoint, graph_state: Annotated[dict, InjectedState]):
    for item in graph_state['solution']:
        if item['group']==data_point.group and item['key']==data_point.key:
            solution_copy=graph_state['solution'].copy()
            solution_copy.remove(item)
            solution_copy+=[data_point.model_dump()]
            graph_state['solution']=solution_copy
            return 'data point updated in solution successfully'
    graph_state['solution']+=[data_point.model_dump()]
    return 'data point added to solution successfully'

add_to_solution_tool=StructuredTool.from_function(
    func=add_to_solution,
    name='add_to_solution',
    description='''
    used to add or update a data point to the solution
    ''',
)


def remove_from_solution(group:str,key:str, graph_state: Annotated[dict, InjectedState]):
    before_removal_count=len(graph_state['solution'])
    graph_state['solution']=[item for item in graph_state['solution'] if item['group']!=group or item['key']!=key]
    after_removal_count=len(graph_state['solution'])
    if before_removal_count==after_removal_count:
        return 'data point not found in solution'
    return 'data point removed from solution successfully'


remove_from_solution_tool=StructuredTool.from_function(
    func=remove_from_solution,
    name='remove_from_solution',
    description='''
    used to remove a data point from the solution
    Args:
        group: The group of the data point
        key: The key of the data point
    ''',
)