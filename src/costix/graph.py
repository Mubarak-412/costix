
import json
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from costix.schemas import (
    AgentOutputSchema,
    CostixState,
    CostixPhase,
    CostixNodes,
    CostixPhaseToNodeMap
    )
from costix.agents import (
    get_info_agent,
    get_solution_agent,
    get_technical_agent,
    get_estimate_agent
)
from costix.model import get_model,get_resoning_model
from costix.tools import get_jupyter_repl_tool,get_display_table_tool
from costix.agents.useCase import fetch_use_case_prompt
    
def create_agent_node(agent:any):
    'creates a graph node from Agent, allows customizing the updates made by agent'

    def node(state:CostixState):
        agent_graph_response=agent.invoke(state)
        structured_response=agent_graph_response.get('structured_response',None)

        updates=agent_graph_response
        if structured_response and isinstance(structured_response,AgentOutputSchema):
            structured_response_json=structured_response.model_dump()
            ai_response={}
            text_response=structured_response_json.get('response',None)
            question_response=structured_response_json.get('question',None)
            if text_response:
                ai_response['text']=text_response
            if question_response:
                ai_response['question']=question_response
            
            ai_message=AIMessage(content=json.dumps(ai_response))
            updates['messages_history'].append(ai_message)
        
        return updates

    return node






ALL_AGENT_NODES=[
    CostixNodes.INFO_AGENT,
    CostixNodes.SOLUTION_AGENT,
    CostixNodes.TECHNICAL_AGENT,
    CostixNodes.ESTIMATE_AGENT,
    ]


class CostixGraph:
    '''
    Graph for the COSTIX estimation process.
    '''

    def __init__(self,checkpointer:any=None):
        model=get_model()
        graph=StateGraph(CostixState)
        
        self.python_tool=get_jupyter_repl_tool()
        self.display_table_tool=get_display_table_tool()
        self.additional_tools=[self.python_tool,self.display_table_tool]
        
        self.info_agent=get_info_agent(model,additional_tools=self.additional_tools)
        self.solution_agent=get_solution_agent(model,additional_tools=self.additional_tools)
        self.technical_agent=get_technical_agent(model,additional_tools=self.additional_tools)
        self.estimate_agent=get_estimate_agent(model,additional_tools=self.additional_tools)


        self.info_agent_node=create_agent_node(self.info_agent)
        self.solution_agent_node=create_agent_node(self.solution_agent)
        self.technical_agent_node=create_agent_node(self.technical_agent)
        self.estimate_agent_node=create_agent_node(self.estimate_agent)

        graph.add_node(CostixNodes.INFO_AGENT,self.info_agent_node)
        graph.add_node(CostixNodes.SOLUTION_AGENT,self.solution_agent_node)
        graph.add_node(CostixNodes.TECHNICAL_AGENT,self.technical_agent_node)
        graph.add_node(CostixNodes.ESTIMATE_AGENT,self.estimate_agent_node)

        graph.add_conditional_edges(START, lambda state:state['current_phase'],CostixPhaseToNodeMap)
        graph.add_edge(ALL_AGENT_NODES,END)
        self.graph=graph.compile(checkpointer=checkpointer)

    def get_graph(self,*args,**kwargs):
            return self.graph.get_graph(*args,**kwargs)

    def initialize_thread(self,thread_id:str,state:CostixState|None=None):

        use_case_id = 'db845027-b985-42d0-8498-62f61f0a7f78'
   
        use_case_prompt = fetch_use_case_prompt(use_case_id=use_case_id)


        initial_state={
            'use_case_prompt': use_case_prompt,
            'current_phase':CostixPhase.INFORMATION_GATHERING,
            'messages':[],
            'thoughts':[],
            'messages_history':[],
            'collected_data':[],
            'solution':[],
            'technical_requirements':[],
            'uploaded_files':[],
            'estimate':[],
            }
        if state:
            initial_state.update(state)
        config={'configurable':{'thread_id':thread_id}}
        # print( f'initializing thread {thread_id} with state {initial_state}')
        self.graph.update_state(config,initial_state)


    def invoke(self,*args,**kwargs):
        'invokes the graph with the given kwargs'
        return self.graph.invoke(*args,**kwargs)
