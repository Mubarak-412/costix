
from typing import Annotated
from langgraph.prebuilt import InjectedState
from langchain.tools import StructuredTool

from costix.schemas import CostixPhase

def update_current_phase(phase: CostixPhase, graph_state: Annotated[dict, InjectedState]):
    """
    Update the current phase of the COSTIX estimation process.
    """

    graph_state["current_phase"] = phase
    return f"Updated current phase to {phase}"




update_current_phase_tool = StructuredTool.from_function(
    func=update_current_phase,
    name="update_current_phase",
    description="Use this tool to update the current phase of the COSTIX estimation process.",
    )