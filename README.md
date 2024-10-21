# Gradio Canvas 🤗

Gradio Canvas is a web application inspired by ChatGPT's Canvas. This project combines the capabilities of Fireworks AI and Instructor to create a seamless code generation experience.

Built with:
- Llama 3.1 405B via [Fireworks AI](https://fireworks.ai)
- [Instructor](https://github.com/instructor-ai/instructor) for structured output parsing
- [Gradio](https://github.com/gradio-app/gradio) for the web interface

## Getting Started

### Prerequisites

- Fireworks AI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gradio-canvas.git
   cd gradio-canvas
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Fireworks AI API key as an environment variable:
   ```bash
   export FIREWORKS_API_KEY=your_api_key_here
   ```

### Usage

Run the application:

    ``` bash
    gradio app.py
    ```
