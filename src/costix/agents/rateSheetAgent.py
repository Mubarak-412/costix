from typing import Annotated, List, TypedDict
from huggingface_hub import Agent
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chat_models.base import BaseChatModel
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState





from costix.tools import (
    web_search_tool,
    get_rate_sheet_vector_store_tool,
    execute_sql_query_tool
    )



RATE_SHEET_AGENT_PROMPT='''

You are a Cloud Pricing Specialist, specializing in providing detailed pricing information for cloud services.
Your process involves utilising different tools and resources to gather accurate pricing data,and presenting the results to help in the process of cost estimation process.

you will be communicating with cost esimation agent and help in providing the pricing information for the user requirements.

**Process:**

1.  **Rate Sheet research :**
    - using the rate sheet knowledge base,search for the relevant rate sheet for the user requirements.
    - utilise the table information and craft the query to fetch the relevant pricing data.
    - present the pricing data to the cost estimation agent in a clear and concise manner carefully including all necessary details.
    - ensure that the query sent to the rate sheet knowledge tool is detailed and capture all the relevant information required to fetch the pricing data


2. **Querying Rate Sheets :**
    - use the execute_sql_query_tool to query the rate sheets
    - present the query results to the cost estimation agent in a clear and concise manner.

2. **Accessing Uploaded Files:**:
    - utilize the python runtime to access the uploaded files and extract the relevant pricing data ( if present).

3. ** Using Web Search Tool:**
    - if the required pricing data is not available in the rate sheet knowledge base,
     use the web_search tool to search for the pricing data.
     present the results to the cost estimation agent mentioning the sources in which the data was found.

#Core Responsibilities:
    - Utilise the rate sheet knowledge base to provide accurate pricing information for cloud services.
    - if the required pricing data is not available in the rate sheet knowledge base,
     inform the cost estimation agent that the pricing data is not available and the sources in which the took up was performed.
    - always provide the source of the pricing data in the response along with the pricing data(for each data point). 


Resources: 
    1. Python runtime : 
        a persistent python runtime that is shared among all the agents.
        used to access user uploaded files and to preform any necessary data processing or analysis.


**Current Context:**
*   `uploaded_files`: 
    - {uploaded_files}
    
'''

promptTemplate=ChatPromptTemplate.from_messages(
    [
        ('system',RATE_SHEET_AGENT_PROMPT),
        MessagesPlaceholder(variable_name='messages'),
    ]

)

rate_sheet_agent_tools=[
    web_search_tool,
    execute_sql_query_tool,
    get_rate_sheet_vector_store_tool(),
]

class RateSheetAgentState(AgentState):
    uploaded_files:List[str]

def get_rate_sheet_agent(model:BaseChatModel,additional_tools:list|None=None,*args,**kwargs):
    ''' creates a instance of rate sheet agent
    
    agrs:
        model: BaseChatModel
            the language model to be used by the agent
        additional_tools: list[BaseTool]
            additional tools to be used by the agent
     '''
    tools=rate_sheet_agent_tools+additional_tools if additional_tools else rate_sheet_agent_tools
    agent= create_react_agent(
        model=model,
        tools=tools,
        prompt=promptTemplate,
        name='rate_sheet_agent',
        state_schema=RateSheetAgentState,
        *args,
        **kwargs
        )
    return agent
    
    


def get_rate_sheet_agent_as_tool(model:BaseChatModel,additional_tools:list|None=None):
    ''' creates a instance of rate sheet agent as a tool
    
    agrs:
        model: BaseChatModel
            the language model to be used by the agent
        additional_tools: list[BaseTool]
            additional tools to be used by the agent
     '''

    rate_sheet_agent=get_rate_sheet_agent(model)

    def talk_to_rate_sheet_agent(query:str,state:Annotated[dict,InjectedState]):
        '''
        communicate with the rate sheet agent and pricing information 
        Args:
            query: str
                the query to be sent to the rate sheet agent
        '''

        query_message=AIMessage(content=query)
        
        rate_sheet_state={'messages':[query_message],'uploaded_files':state.get('uploaded_files','')}

        response=rate_sheet_agent.invoke(rate_sheet_state)
        return response['messages'][-1].content
    
    return talk_to_rate_sheet_agent

