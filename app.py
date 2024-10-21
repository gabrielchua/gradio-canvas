"""
app.py
"""

# Standard library imports
import json
from typing import Tuple

# Third-party imports
import gradio as gr
import instructor
from fireworks.client import Fireworks
from pydantic import BaseModel, ValidationError

# Local imports
from config import (
    APP_HEADER,
    APP_TITLE,
    FIREWORKS_API_KEY,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_SYSTEM_PROMPT,
)


# Initialize Instructor with the Fireworks client
client = Fireworks(api_key=FIREWORKS_API_KEY)
client = instructor.from_fireworks(client)


# Define response models for feedback and code using Pydantic
class CodeResponse(BaseModel):
    """Code Response"""

    planning: str
    full_python_code: str
    commentary: str


def get_llm_responses(
    user_input: str, conversation: list, current_code: str = None
) -> Tuple[list, str, str]:
    """
    Generates feedback and code based on user input using the Instructor LLM.

    Args:
        user_input (str): The input text from the user.
        conversation (list): The conversation history.
        current_code (str, optional): Existing code if any.

    Returns:
        Tuple[list, str, str]: A tuple containing updated conversation, generated code, and formatted conversation history.
    """
    try:
        # Update conversation history with user input
        conversation.append(
            {
                "role": "user",
                "content": (
                    user_input
                    if current_code is None
                    else f"{user_input} And here is the existing code: {current_code}"
                ),
            }
        )

        # Generate Feedback
        feedback_resp = client.chat.completions.create(
            model=LLM_MODEL,
            response_model=CodeResponse,
            max_tokens=LLM_MAX_TOKENS,
            messages=conversation,
        )

        code = feedback_resp.full_python_code

        # Update conversation history with assistant response
        conversation.append(
            {
                "role": "assistant",
                "content": feedback_resp.model_dump_json(),
            }
        )

        # Format conversation history for display
        conversation_text = ""

        conversation_to_print = conversation[1:]

        round_number = (
            len(conversation_to_print) // 2
        )  # Assuming each round has a user and assistant message

        # Add the latest conversation pair to the top
        if len(conversation_to_print) >= 2:
            latest_pair = conversation_to_print[-2:]
            conversation_text += f"## Version {round_number}\n\n"
            for message in latest_pair:
                if message["role"] != "system":
                    role = message["role"].capitalize()
                    try:
                        content = json.loads(message["content"])
                        content = content["commentary"]
                    except:
                        content = message["content"].split(
                            " And here is the existing code:"
                        )[0]
                        if content == "":
                            content = "_User edited the code directly_"

                    emoji = "👤" if role == "User" else "🤖"
                    conversation_text += f"**{emoji} {role}:** {content}\n\n"

        # Add the rest of the conversation history
        for i, message in enumerate(conversation_to_print[:-2]):
            if message["role"] != "system":
                if i % 2 == 0:
                    round_number = (len(conversation_to_print) - i) // 2
                    conversation_text += f"## Version {round_number-1}\n\n"

                role = message["role"].capitalize()
                try:
                    content = json.loads(message["content"])
                    content = content["commentary"]
                except:
                    content = message["content"].split(
                        " And here is the existing code:"
                    )[0]
                    if content == "":
                        content = "_User edited the code directly_"

                emoji = "👤" if role == "User" else "🤖"
                conversation_text += f"**{emoji} {role}:** {content}\n\n"

        return conversation, code, conversation_text

    except ValidationError as ve:
        error_msg = f"Response validation error: {ve}"
        raise gr.Error(error_msg)
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        raise gr.Error(error_msg)


# Define the Gradio interface
with gr.Blocks(
    title=APP_TITLE, theme=gr.themes.Ocean(), fill_width=True, fill_height=True
) as demo:
    gr.HTML(APP_HEADER)

    with gr.Row():
        with gr.Column(scale=1):
            conversation_output = gr.Markdown(label="Chat History", height=500)

        with gr.Column(scale=2):
            code_output = gr.Code(
                label="LLM Generated Code",
                interactive=True,
                language="python",
                lines=30,
            )
            with gr.Row():
                add_comments_btn = gr.Button("Add Comments 💬")
                refactor_btn = gr.Button("Refactor 🔨")

    with gr.Row():
        with gr.Column(scale=9):
            user_input = gr.Textbox(
                label="Enter Your Request here",
                placeholder="Type something here...",
                lines=2,
            )
        with gr.Column(scale=1):
            submit_btn = gr.Button("Submit 🚀")
            reset_btn = gr.Button("Reset 🔄")

    # Initialize conversation history with system prompt using Gradio State
    initial_conversation = [
        {
            "role": "system",
            "content": LLM_SYSTEM_PROMPT,
        }
    ]

    conversation_state = gr.State(
        initial_conversation
    )  # Define a single State instance

    # Define the button click event
    def on_submit(user_input, conversation, current_code):
        result = get_llm_responses(user_input, conversation, current_code)
        return [""] + list(result)  # Clear the textbox by returning an empty string

    submit_btn.click(
        fn=on_submit,
        inputs=[user_input, conversation_state, code_output],
        outputs=[user_input, conversation_state, code_output, conversation_output],
    )

    def add_comments_fn(conversation, current_code):
        return on_submit(
            "Please add more comments to the code. Make it production ready.",
            conversation,
            current_code,
        )

    add_comments_btn.click(
        fn=add_comments_fn,
        inputs=[conversation_state, code_output],
        outputs=[user_input, conversation_state, code_output, conversation_output],
    )

    def refactor_fn(conversation, current_code):
        return on_submit(
            "Please refactor the code. Make it more efficient.",
            conversation,
            current_code,
        )

    refactor_btn.click(
        fn=refactor_fn,
        inputs=[conversation_state, code_output],
        outputs=[user_input, conversation_state, code_output, conversation_output],
    )

    def reset_fn():
        return "", initial_conversation, "", ""

    reset_btn.click(
        fn=reset_fn,
        outputs=[user_input, conversation_state, code_output, conversation_output],
    )

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch()
