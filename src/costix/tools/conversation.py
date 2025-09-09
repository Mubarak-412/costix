import json
from typing import Annotated, Optional
from enum import StrEnum
from langchain_core.messages import AIMessage
from langgraph.graph import END
from pydantic import BaseModel,Field
from costix.schemas import QuestionSchema
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command



class ConversationSchema(BaseModel):
    response:Optional[Annotated[str,Field(description='text response to be send to the user')]]
    question:Optional[QuestionSchema]

def handle_conversation(
        conversation:ConversationSchema,
        tool_call_id: Annotated[str, InjectedToolCallId],
        agent_state: Annotated[dict, InjectedState],
    ):
    '''
    used to interact with the user, either by presenting a question or by displaying a text response
    '''
    generated_text_response=conversation.response or None
    generated_question=conversation.question.model_dump() if conversation.question else None

    if not generated_text_response and not generated_question:
        return 'Error: coversation tool requires either a question or a text response'
    generated_response={
        'text':generated_text_response,
        'question':generated_question
    }

    response_content=json.dumps(generated_response)       
    response_message=AIMessage(response_content)
    tool_message=ToolMessage('message successfully displayed',tool_call_id=tool_call_id)
    messages=agent_state['messages']
    messages_history=agent_state['messages_history']

    new_updates={
        'messages':messages+[tool_message],
        'messages_history':messages_history+[response_message]
    }
    updates=agent_state.copy()
    updates.update(new_updates)
    return Command(
        update=updates,
        graph=Command.PARENT,
        goto=END)


conversation_tool=StructuredTool.from_function(
    func=handle_conversation,
    name='conversation_tool',
    description='used to interact with the user, either by presenting a question or by displaying a text response',
)