
from langgraph.graph import StateGraph, START, END
from costix.schemas import CostixState,CostixPhase,CostixNodes

from costix.agents import get_info_agent
from costix.model import get_model 
    
def create_agent_node(agent:any):
    'creates a graph node from Agent, allows customizing the updates made by agent'

    def node(state:CostixState):
        response=agent.invoke(state)
        messages=response['messages']
        return {'messages':messages}

    return node



phaseToNodeMap={
    CostixPhase.INFORMATION_GATHERING:CostixNodes.INFO_AGENT,
}


ALL_AGENT_NODES=[CostixNodes.INFO_AGENT]


class CostixGraph:
    '''
    Graph for the COSTIX estimation process.
    '''

    def __init__(self,checkpointer:any=None):
        model=get_model()
        graph=StateGraph(CostixState)
        self.info_agent=get_info_agent(model)
        graph.add_node(CostixNodes.INFO_AGENT,create_agent_node(self.info_agent))
        graph.add_conditional_edges(START, lambda state:state['current_phase'],phaseToNodeMap)
        graph.add_edge(ALL_AGENT_NODES,END)
        self.graph=graph.compile(checkpointer=checkpointer)


    def initialize_thread(self,thread_id:str):
        initial_state={
            'current_phase':CostixPhase.INFORMATION_GATHERING,
            'messages':[],
            'messages_history':[],
            'collected_data':[],
            'uploaded_files':[],
            }
        config={'configurable':{'thread_id':thread_id}}
        self.graph.update_state(config,initial_state)


    def invoke(self,*args,**kwargs):
        'invokes the graph with the given kwargs'
        return self.graph.invoke(*args,**kwargs)
