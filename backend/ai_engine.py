import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ---------------------------
# Utility: Clean Markdown Code
# ---------------------------
def clean_code_output(text: str):
    """
    Removes markdown code block formatting like:
    ```python
    code
    ```
    """
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last line (``` blocks)
        if len(lines) > 2:
            text = "\n".join(lines[1:-1])
    return text.strip()


# ---------------------------
# Run Code (Explain / Improve)
# ---------------------------
def generate_code(prompt: str):
    try:
        response = client.chat.completions.create(
             model="llama-3.3-70b-versatile",   # Updated working model
            messages=[
                {
                    "role": "system",
                    "content": "You are a coding assistant. Return only raw code. Do NOT use markdown. Do NOT wrap in triple backticks."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
        )

        raw_output = response.choices[0].message.content
        return clean_code_output(raw_output) if raw_output else ""

    except Exception as e:
        return f"❌ Groq API Error: {str(e)}"


# ---------------------------
# Debug Code
# ---------------------------
def debug_code(code: str):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # Updated working model
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional debugger. Fix the code and return ONLY the corrected code. Do NOT use markdown formatting."
                },
                {
                    "role": "user",
                    "content": f"Debug this code:\n\n{code}"
                }
            ],
            temperature=0.3,
        )

        raw_output = response.choices[0].message.content
        return clean_code_output(raw_output) if raw_output else ""

    except Exception as e:
        return f"❌ Groq API Error: {str(e)}"
