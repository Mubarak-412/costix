
from typing import Annotated
from langchain.tools import StructuredTool
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from costix.chains import get_evaluator_chain
from costix.model import get_model
from costix.schemas import CostixPhase,CostixPhaseToNodeMap


AI_MODEL=get_model()
EVALUATOR_CHAIN=get_evaluator_chain(AI_MODEL)

def update_current_phase(
    phase: CostixPhase,
    tool_call_id: Annotated[str, InjectedToolCallId], 
    agent_state: Annotated[dict, InjectedState]):
    """
    Update the current phase of the COSTIX estimation process.
    """

    current_phase=agent_state['current_phase']
    if current_phase==phase:
        return f"Phase {phase} is already the current phase."

    next_node=CostixPhaseToNodeMap[phase]
    
    if not next_node:
        return f"Phase {phase} is not a valid phase."

    current_agent_messages=agent_state['messages']
    evaluator_messages=current_agent_messages[:-1]                 # removing the current toolcall ai message to avoid error
    evaluator_response=EVALUATOR_CHAIN.invoke(
        {**agent_state,'messages':evaluator_messages,'destination_phase':phase}
    )
    evaluation_response=evaluator_response
    
    if evaluation_response.result!='ACCEPT':
        reject_message=f"Transition to {phase} was rejected. Feedback: {evaluation_response.feedback}"
        print(evaluation_response,reject_message)
        return reject_message

    thought=f'Moving to {phase} Phase'
    tool_message=ToolMessage(content=f"Updated current phase to {phase}",tool_call_id=tool_call_id)


    # this update sends the current state of the agent to the next agent ( different than a agent updating its state)
    current_agent_messages=agent_state['messages']
    updates_to_apply={
        'current_phase':phase,
        'messages':current_agent_messages+[tool_message],
        'thoughts':[thought]
    }
    new_state=agent_state.copy()
    new_state.update(updates_to_apply)
    return Command(
        update=new_state,
        graph=Command.PARENT,
        goto=next_node,
        )





update_current_phase_tool = StructuredTool.from_function(
    func=update_current_phase,
    name="update_current_phase",
    description="Use this tool to update the current phase of the COSTIX estimation process.",
    )