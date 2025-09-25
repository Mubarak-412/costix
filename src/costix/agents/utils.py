
from typing import Optional
from langchain.tools import tool
from langchain_core.messages import AIMessage
from langchain_core.prompts import prompt
from langgraph.graph import END
from pydantic import BaseModel, Field
from costix.schemas import CostixAgentState
from langgraph.prebuilt import create_react_agent, tools_condition
from costix.schemas import AgentOutputSchema




def create_costix_agent(model:BaseModel,tools:list[tool],prompt:prompt, *args,**kwargs):
    '''
    Create a generic agent for costix. 
    that has the CostixState  and disables parallel tool calls.

    - parallel tool calls are disabled to ensure that there is only one change to state
    '''

    
    agent= create_react_agent(
        model=model,
        prompt=prompt,
        tools=tools,
        state_schema=CostixAgentState,
        response_format=AgentOutputSchema,
        *args,
        **kwargs
        )
    return agent





