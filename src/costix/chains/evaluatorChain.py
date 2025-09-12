from typing import List, Literal, Union
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chat_models.base import BaseChatModel
from langgraph.prebuilt import create_react_agent
from pandas.io.common import Any
from pydantic import BaseModel, Field
from costix.schemas import CostixAgentState







class EvaluationResult(BaseModel):
    '''
    the result of the evaluation
    '''
    result:Union[Literal['ACCEPT'],Literal['REJECT']]=Field(description='the result of the evaluation')
    feedback:List[str]=Field(description='the feedback for the evaluation,required for REJECT result')




EVALUATOR_PROMPT='''

you are a evaluator agent in a multi agent  cost estimation system,
you role is to oversee the the flow of control between the other agents,
and ensure that the cost estimation process is completed successfully.

the cost estimation process consist of the following:

    1. INFORMATION_GATHERING phase: 
        responsible for gathering the requirements for the project
    2. SOLUTION_GENERATION phase:
        responsible for creating a high level solution that captures all the requirements
    3. TECHNICAL phase:
        responsible for identifying all the necessary resources/components for implementing the project
            example: quantities ,instance sizes, storage types, network components
    4. ESTIMATION phase:
        responsible for estimating the cost of the project based on the requirements and the resources/components identified in the TECHNICAL phase
        provides the final cost of the project using the right rate sheets available in ESTIMATION phase

additional information:
    all agents have a shared python runtime that allows them to access the user uploaded files and perform calculations and generate custom reports.

Key Respnsibilities:
    1. Ensuring that all the the requirements are captured and integrated into the project
    2. Ensuring that proper flow of control takes place by transiting to proper phase
    3. when requirements are changed , make sure that the changes are reflected throught all the phases and existing plans are modified to capture the changes
    4. provide feed back to  the agent in case of any errors or issues that arise during the estimation process


currently trying to transition from {current_phase} to {destination_phase}


**current context:**

    *data collected in INFORMATION_GATHERING phase:*
        {collected_data}
 
    *SOLUTION generated:*
        {solution}

    *TECHNICAL requirements:*
        {technical_requirements}

    *ESTIMATE:*
        []          

'''

promptTemplate=ChatPromptTemplate.from_messages(
    [
        ('system',EVALUATOR_PROMPT),
        MessagesPlaceholder(variable_name='messages'),
    ]

)


def get_evaluator_chain(model:BaseChatModel):
    ''' creates a instance of evaluator agent
    
    agrs:
        model: BaseChatModel
            the language model to be used by the agent
     '''
    
    evaluator_chain=  promptTemplate | model.with_structured_output(EvaluationResult)
    return evaluator_chain
    
    
