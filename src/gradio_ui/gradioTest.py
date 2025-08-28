import json
import gradio as gr
from enum import StrEnum
from pydantic import BaseModel, Field
from typing import List, Tuple

# --- User-Provided Schemas ---
# The schema for the question types, as provided in the prompt.
class QuestionTypes(StrEnum):
    """
    The type of question to ask the user
    """
    SINGLE_SELECT = 'single_select'
    MULTI_SELECT = 'multi_select'
    TEXT = 'text'

# The schema for the question itself.
class QuestionSchema(BaseModel):
    """
    The Question that should be asked to the user
    """
    title: str = Field(..., description='The title of the question')
    subtitle: str = Field(..., description='The subtitle of the question')
    type: QuestionTypes = Field(..., description='The type of the question to ask the user')
    options: List[str] = Field([], description='The options for the question')

# --- Helper Functions and Gradio Logic ---

# A simple list of sample questions to demonstrate all types.
QUESTIONS = [
    QuestionSchema(
        title="What's your favorite coding language?",
        subtitle="Choose one from the list below.",
        type=QuestionTypes.SINGLE_SELECT,
        options=["Python", "JavaScript", "C++", "Rust"]
    ),
    QuestionSchema(
        title="What are your favorite hobbies?",
        subtitle="Select all that apply.",
        type=QuestionTypes.MULTI_SELECT,
        options=["Reading", "Hiking", "Gaming", "Cooking"]
    ),
    QuestionSchema(
        title="Tell us about yourself",
        subtitle="Provide a brief description in the text box below.",
        type=QuestionTypes.TEXT,
        options=[]
    ),
]

# State to track the current question index. It is initialized to 1 because
# the first question (index 0) will be displayed on load.
question_idx = 1

# Function to generate the Gradio component based on the question schema.
def create_question_component(question: QuestionSchema):
    """
    Generates a Gradio component block to be displayed in the chatbot.
    This function acts as a wrapper to render the correct UI for each question type.
    """
    # Create a Gradio Blocks to act as the container for the custom component.
    # This allows for more complex layouts than just a single component.
    with gr.Blocks() as component_block:
        gr.Markdown(f"## {question.title}")
        gr.Markdown(f"### {question.subtitle}")
        
        # Use a switch-case-like structure to render the correct component.
        if question.type == QuestionTypes.SINGLE_SELECT:
            gr.Radio(
                choices=question.options,
                label="Your choice",
                interactive=True,
            )
        elif question.type == QuestionTypes.MULTI_SELECT:
            gr.CheckboxGroup(
                choices=question.options,
                label="Your choices",
                interactive=True,
            )
        elif question.type == QuestionTypes.TEXT:
            gr.Textbox(
                label="Your answer",
                placeholder="Type your response here...",
                interactive=True,
            )
        
        # Add a submit button for the question. In a real app, this would
        # capture the user's input and proceed to the next step.
        gr.Button("Submit Answer")

    return component_block

# Function to update the chat history with the next question.
def append_next_question(chat_history: List[gr.ChatMessage]):
    """
    Displays the next question in the chatbot and updates the state.
    """
    global question_idx
    
    # Get the next question from the predefined list.
    question = QUESTIONS[question_idx % len(QUESTIONS)]
    
    # Create the custom Gradio component for the current question.
    question_component = create_question_component(question)
    
    # Add the new question component to the chat history.
    # The first element of the tuple is the user message (empty in this case),
    # and the second is the bot message (the custom Gradio component).
    chat_history.append(gr.ChatMessage(role='assistant',content=question_component))
    
    # Move to the next question index.
    question_idx += 1
    
    return chat_history

# --- Gradio App Interface ---
with gr.Blocks(theme=gr.themes.Base()) as demo:
    gr.Markdown("<h1>Gradio Chatbot with Dynamic Questions</h1>")

    # Initial dummy conversation and the first question.
    initial_history = [
        gr.ChatMessage(role='user',content='Hello there!'),
        gr.ChatMessage(role='assistant',content='Hello! I am a question bot. Let\'s get started.'),
        gr.ChatMessage(role='assistant',content=create_question_component(QUESTIONS[0])) # The first question (index 0)
    ]

    # The gr.Chatbot component is what displays the messages.
    # We use type='messages' and initialize it with the dummy history.
    chatbot = gr.Chatbot(
        label="Question Bot",
        type="messages",
        value=[],
    )
    
    # A simple button to trigger the next question.
    next_btn = gr.Button("Next Question")

    # Layout the components.
    # with gr.Row():
    #     chatbot.render()

    # Define the event handler for the "Next Question" button.
    # It takes the current chatbot history, calls `append_next_question` to get the updated history,
    # and then updates the chatbot component.
    next_btn.click(
        fn=append_next_question,
        inputs=[chatbot],
        outputs=[chatbot]
    )

if __name__ == "__main__":
    demo.launch()
