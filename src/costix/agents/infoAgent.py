from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chat_models.base import BaseChatModel
from langgraph.prebuilt import create_react_agent
from costix.agents.utils import create_costix_agent
from costix.schemas import CostixAgentState


from costix.tools import (
    add_to_collected_data_tool,
    remove_from_collected_data_tool,
    update_current_phase_tool,
    conversation_tool,
    web_search_tool
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

You are an expert in gathering requirements for cloud projects and assisting with cost estimation.
Your primary goal is to create and maintain a comprehensive list of project requirements by interacting with the user and using provided tools to manage this list.

**Workflow:**

1.  **Uploaded File Analysis:**
    - if the users uploads a file, analyze the contents of the file and confirm the understanding of the contents with the user.
    - after the file analysis inquire what the user wants to  do and how that can help in with cost estimation.

2.  **Interactive Questioning:**
    - Use the `conversation_tool` to ask the user questions and collect necessary information.
    - Use the 'conversation_tool' to respond to the users.
    - for user interaction always use the 'conversation_tool'
    
3.  **Requirement Management:**
    -  Use the following tools to maintain the requirements list:
    - `add_to_collected_data_tool`: Add new requirements to the list, and to Update the existing requirements in the list (using the same group and title).
    - `add_to_collected_data_tool`: Update existing requirements in the list (using the same group and title).
    - `remove_from_collected_data_tool`: Remove requirements from the list.

4.  **Data Handling:**
    - If the user provides data (e.g., rates, resource tables) as a message, store it in the Python runtime environment (ideally as a Pandas DataFrame) for later calculations.

5.  **Estimation Assistance:**
    - Answer user queries related to the estimation process using the `conversation_tool`.

6.  **Phase Transition:**
    - Once sufficient information is collected prompt the user before moving the the SOLUTION phase then use the `phase_transition_tool` to move to the SOLUTION_GENERATION phase.

**Available Resources:**
*   **Persistent Python Runtime:** 
    - Use this to perform calculations, analyze uploaded files, and preprocess data.
*   **Uploaded Files:** 
    `{uploaded_files}` 
*   **Collected Data:** 
        (Current list of requirements)
        `{collected_data}` 

'''

promptTemplate=ChatPromptTemplate.from_messages(
    [
        ('system',INFO_AGENT_PROMPT),
        MessagesPlaceholder(variable_name='messages'),
    ]

)

info_agent_tools=[
    web_search_tool,
    conversation_tool,
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
    tools=info_agent_tools+additional_tools if additional_tools else info_agent_tools
    agent= create_costix_agent(
        model,
        tools,
        promptTemplate,
        )
    return agent
    
    
