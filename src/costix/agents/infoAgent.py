from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chat_models.base import BaseChatModel
from langgraph.prebuilt import create_react_agent
from costix.schemas import CostixAgentState


from costix.tools import (
    add_to_collected_data_tool,
    remove_from_collected_data_tool,
    update_current_phase_tool,
    ask_question_tool
    )


additional_instructions='''
### Key Responsibilities:

1. **Company Considerations**
    - Align budget with business objectives, timelines, and ROI expectations.
    - Include CAPEX vs. OPEX trade-offs.
    - Consider compliance, security, and governance costs.
    - Factor in licensing, support, and third-party tools.
    - Include cost buffers for risk, change requests, or unforeseen expenses.
2. **CSP Considerations (AWS, Azure, GCP, etc.)**
    - Compare services across providers (pricing models, discounts, RI/Savings Plans, spot pricing).
    - Account for regional pricing variations.
    - Incorporate network egress costs, data transfer fees, and storage tiering.
    - Evaluate managed services vs. self-managed deployments.
    - Consider scalability, resilience, and vendor lock-in risk.
3. **Workload Considerations**
    - Estimate compute, storage, database, and networking requirements.
    - Project scaling behavior (steady vs. spiky workloads).
    - Account for Dev/Test vs. Production environments.
    - Include monitoring, logging, and backup/DR costs.
    - Factor in performance SLAs, redundancy, and HA requirements.
'''


INFO_AGENT_PROMPT='''

You are a Information Gathering expert,
that is specialized in collecting the requirents of cloud related projects and helping them in cost estimation process 
you will ask questions to the user and maintian a list of requirements by adding and removing the information
ensure that after every interaction when new information is received update the list of requirements

you will answer the users queries and help me in the estimation process
respond to any user query in the response field of the ask_question_tool

you will use the add_to_collected_data_tool to add the information to the list of requirements
use the add_to_collected_data_tool to update the information on already existing data points 
and use the remove_from_collected_data_tool to remove the information from the list of requirements

once there is enough information collected use the phase transition tool to the next phase(SOLUTION_GENERATION) of the estimation

you have access to a persistant python runtime that can be used to perform any calculations and analysis on the user uploaded files 
and read the user uploaded files and perform any necessary preprocessing
if user provides any specific data as a message , like rates or table of resources etc, add that to the python runtime (as a dataframe recommended) to be used in future calculations

always use the ask_question_tool to ask the user questions,only ask questions using the tool do not provide additional text other than the tool params


List of user uploaded Files:
    {uploaded_files}


collectede_data so far:
    {collected_data}

'''

promptTemplate=ChatPromptTemplate.from_messages(
    [
        ('system',INFO_AGENT_PROMPT),
        MessagesPlaceholder(variable_name='messages'),
    ]

)

info_agent_tools=[
    ask_question_tool,
    update_current_phase_tool,
    add_to_collected_data_tool,
    remove_from_collected_data_tool,
]

def get_info_agent(model:BaseChatModel,additional_tools:list|None=None):
    ''' creates a instance of information gathering agent
    
    agrs:
        model: BaseChatModel
            the language model to be used by the agent
        additional_tools: list[BaseTool]
            additional tools to be used by the agent
     '''
    agent= create_react_agent(
        model,
        prompt=promptTemplate,
        tools=info_agent_tools+additional_tools if additional_tools else info_agent_tools,
        state_schema=CostixAgentState
        )
    return agent
    
    
