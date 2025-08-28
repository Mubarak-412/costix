import gradio as gr
from costix.schemas import QuestionSchema,QuestionTypes


def create_question_component(question: QuestionSchema,on_select=None):
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
            single_select=gr.Radio(
                choices=question.options,
                label="Your choice",
                interactive=True,
            )
            single_select.change(on_select if on_select else None,inputs=[single_select])

        elif question.type == QuestionTypes.MULTI_SELECT:
            multi_select=gr.CheckboxGroup(
                choices=question.options,
                label="Your choices",
                interactive=True,
            )
            confirm_btn=gr.Button("confirm")
            confirm_btn.click(on_select if on_select else None,inputs=[multi_select])
        elif question.type == QuestionTypes.TEXT:
            textbox=gr.Textbox(
                label="Your answer",
                placeholder="Type your response here...",
                interactive=True,
            )
        
        # Add a submit button for the question. In a real app, this would
        # capture the user's input and proceed to the next step.
        # gr.Button("Submit Answer")

    return component_block