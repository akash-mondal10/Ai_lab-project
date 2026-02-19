from dotenv import load_dotenv
import os
import ast

load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

from interactive_executor import InteractiveExecutor

# ==========================
# App Setup
# ==========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ==========================
# Request Models
# ==========================

class RunRequest(BaseModel):
    code: str
    stdin: str = ""

class GenerateRequest(BaseModel):
    prompt: str


# ==========================
# RUN (HTTP)
# ==========================

@app.post("/run")
def run_code(request: RunRequest):
    executor = InteractiveExecutor(request.code)

    if request.stdin:
        executor.write(request.stdin)

    result = executor.read()

    return {"output": result}


# ==========================
# DEBUG (SMART + STABLE)
# ==========================

@app.post("/debug")
def debug_code(request: RunRequest):

    result = ""
    needs_fix = False

    # ------------------------
    # Step 1: Syntax check
    # ------------------------
    try:
        ast.parse(request.code)
    except SyntaxError as e:
        result = f"SyntaxError: {str(e)}"
        needs_fix = True

    # ------------------------
    # Step 2: Runtime check
    # ------------------------
    if not needs_fix:
        executor = InteractiveExecutor(request.code)

        if request.stdin:
            executor.write(request.stdin)

        result = executor.read()

        if any(keyword in result for keyword in [
            "Traceback",
            "Error",
            "Exception",
            "SyntaxError"
        ]):
            needs_fix = True

    # ------------------------
    # Step 3: If no issue
    # ------------------------
    if not needs_fix:
        return {
            "output": result,
            "fixed_code": None
        }

    # ------------------------
    # Step 4: Send to LLM
    # ------------------------

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert Python compiler. "
                    "Fix ALL syntax and runtime errors. "
                    "Return ONLY valid runnable Python code. "
                    "No explanation. No markdown."
                )
            },
            {
                "role": "user",
                "content": f"""
Fix this Python code:

{request.code}

It produced this error/output:

{result}
"""
            }
        ],
        temperature=0
    )

    fixed_code = (response.choices[0].message.content or "").strip()

    # Remove markdown if present
    if fixed_code.startswith("```"):
        lines = fixed_code.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        fixed_code = "\n".join(lines).strip()

    return {
        "output": result,
        "fixed_code": fixed_code
    }


# ==========================
# GENERATE
# ==========================

@app.post("/generate")
def generate_code(request: GenerateRequest):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional Python developer. "
                    "Write clean, correct, runnable Python code. "
                    "Return ONLY Python code. No explanation."
                )
            },
            {
                "role": "user",
                "content": request.prompt
            }
        ],
        temperature=0.3
    )

    generated_code = (response.choices[0].message.content or "").strip()

    if generated_code.startswith("```"):
        lines = generated_code.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        generated_code = "\n".join(lines).strip()

    return {"code": generated_code}


# ==========================
# WEBSOCKET (INTERACTIVE RUN)
# ==========================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    executor = None

    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "run":
                executor = InteractiveExecutor(data["code"])
                await websocket.send_text("Process started\n")

            elif data["type"] == "input":
                if executor:
                    executor.write(data["input"] + "\n")

            if executor:
                output = executor.read()
                if output:
                    await websocket.send_text(output)

    except WebSocketDisconnect:
        print("Client disconnected")
