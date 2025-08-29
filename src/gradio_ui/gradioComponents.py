from typing import TypedDict
import gradio as gr
from costix.schemas import QuestionSchema,QuestionTypes


class QuestionJson(TypedDict):
    title:str
    subtitle:str
    type:QuestionTypes
    options:list[str]


def create_question_component(question: QuestionJson,on_select=None):
    """
    Generates a Gradio component block to be displayed in the chatbot.
    This function acts as a wrapper to render the correct UI for each question type.
    """
    # Create a Gradio Blocks to act as the container for the custom component.
    # This allows for more complex layouts than just a single component.
    with gr.Blocks() as component_block:
        gr.Markdown(f"## {question.get('title','')}")
        gr.Markdown(f"### {question.get('subtitle','')}")
        # Use a switch-case-like structure to render the correct component.
        if question.get('type') == QuestionTypes.SINGLE_SELECT:
            single_select=gr.Radio(
                id='single_select',
                choices=question.get('options',[]),
                label="Your choice",
                interactive=True,
            )
            single_select.change(fn=on_select if on_select else None,inputs=[single_select])

        elif question.get('type') == QuestionTypes.MULTI_SELECT:
            multi_select=gr.CheckboxGroup(
                id='multi_select',
                choices=question.get('options',[]),
                label="Your choices",
                interactive=True,
            )
            confirm_btn=gr.Button("confirm")
            confirm_btn.click(fn=on_select if on_select else None,inputs=[multi_select])
        elif question.get('type') == QuestionTypes.TEXT:
            textbox=gr.Textbox(
                id='textbox',
                label="Your answer",
                placeholder="Type your response here...",
                interactive=True,
            )
        
        # Add a submit button for the question. In a real app, this would
        # capture the user's input and proceed to the next step.
        # gr.Button("Submit Answer")

    return component_block