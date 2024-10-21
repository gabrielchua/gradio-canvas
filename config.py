"""
constants.py
"""

import os

APP_TITLE = "🤗 Gradio Canvas"

APP_HEADER = """
<div style="text-align: center;">
    <h1>🤗 Gradio Canvas</h1>
    <p> Powered by <a href="https://fireworks.ai">Fireworks AI</a> 🎆 and <a href="https://github.com/instructor-ai/instructor">Instructor</a> 👨‍🏫</p>
</div>
"""

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")

LLM_MAX_TOKENS = 16_384

LLM_MODEL = "accounts/fireworks/models/llama-v3p1-405b-instruct"

LLM_SYSTEM_PROMPT = """
Your goal is to generate Python code based on the user's request. 

You will receive a user request and optionally some existing code.

You MUST return your response as a JSON with the following fields: `planning`, `full_python_code`, `commentary`. 

The `full_python_code` should be a complete Python script that can be executed - no code blocks or other formatting.
"""
