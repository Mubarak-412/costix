from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chat_models.base import BaseChatModel
from langgraph.prebuilt import create_react_agent
from costix.schemas import CostixAgentState


from costix.tools import (
    update_current_phase_tool,
    ask_question_tool,
    add_to_solution_tool,
    remove_from_solution_tool
    )


SOLUTION_AGENT_PROMPT='''

You are an expert Cloud Solution Architect ,
that is specialized in providing cloud solutions to the user
you will take the user requirements and provide a cloud solution that meets the requirements
you will generate the Overall Solution Summary based on the users requirements

for further clarification and confirmation you will ask questions to the user

you will ask questions to the user and maintian a solution summary by adding and removing the information
you will use the add_to_solution_tool to add the information to the list of solution requirements
use the add_to_solution_tool to update the information on already existing data points 
and use the remove_from_solution_tool to remove the information from the list of requirements

once there is enought information collected use the phase transition tool to the next phase of the estimation

you have access to a persistant python runtime that can be used to perform any calculations and analysis on the user uploaded files 
and read the user uploaded files and perform any necessary preprocessing

always use the ask_question_tool to ask the user questions,only ask questions using the tool do not provide additional text other than the tool params

List of user uploaded Files:
    {uploaded_files}


'''

promptTemplate=ChatPromptTemplate.from_messages(
    [
        ('system',SOLUTION_AGENT_PROMPT),
        MessagesPlaceholder(variable_name='messages'),
    ]

)

solution_agent_tools=[
    add_to_solution_tool,
    remove_from_solution_tool,
    update_current_phase_tool,
    ask_question_tool
]

def get_solution_agent(model:BaseChatModel,additional_tools:list|None=None):
    ''' creates a instnce of solution agent
    
    agrs:
        model: BaseChatModel
            the language model to be used by the agent
     '''
    agent= create_react_agent(
        model,
        prompt=promptTemplate,
        tools=solution_agent_tools+additional_tools if additional_tools else solution_agent_tools,
        state_schema=CostixAgentState
        )
    return agent
    
    
