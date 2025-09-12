
from langchain.tools import tool
from langchain_core.prompts import prompt
from pydantic import BaseModel
from costix.schemas import CostixAgentState
from langgraph.prebuilt import create_react_agent

def create_costix_agent(model:BaseModel,tools:list[tool],prompt:prompt, *args,**kwargs):
    
    model_with_tools=model.bind_tools(tools=tools,parallel_tool_calls=False) if tools else model
    agent= create_react_agent(
        model=model_with_tools,
        prompt=prompt,
        tools=tools,
        state_schema=CostixAgentState,
        *args,
        **kwargs
        )
    return agent