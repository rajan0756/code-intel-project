"""
AI-Driven Code Intelligence & Automated Documentation System — Backend

Run with:
    uvicorn main:app --reload --port 8000
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from prompts import explanation_prompt, diagram_prompt, docs_prompt
from ai_client import call_ai

app = FastAPI(title="AI Code Intelligence API")

# Allow the frontend (running on a different port/origin) to call this API.
# Tighten this before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_CODE_CHARS = 20000  # keep prompts within reasonable size for hackathon demo


class AnalyzeResponse(BaseModel):
    filename: str
    explanation: str
    mermaid_diagram: str
    documentation: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(file: UploadFile = File(...)):
    raw = await file.read()

    try:
        code = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be plain text source code (UTF-8).")

    if not code.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(code) > MAX_CODE_CHARS:
        code = code[:MAX_CODE_CHARS]  # truncate for demo purposes; note this to the user in the UI

    filename = file.filename or "code.py"

    # Run all three AI calls. Sequential for simplicity/reliability in a hackathon demo;
    # switch to asyncio.gather if you want them in parallel and your AI client supports async.
    explanation = call_ai(explanation_prompt(code, filename))
    mermaid_diagram = call_ai(diagram_prompt(code, filename))
    documentation = call_ai(docs_prompt(code, filename))

    return AnalyzeResponse(
        filename=filename,
        explanation=explanation,
        mermaid_diagram=_clean_mermaid(mermaid_diagram),
        documentation=documentation,
    )


def _clean_mermaid(text: str) -> str:
    """
    Clean AI-generated Mermaid output so it renders without parse errors.
    Handles: code fences, quoted strings inside node labels, special chars.
    """
    import re

    text = text.strip()

    # 1. Strip markdown code fences (```mermaid ... ``` or ``` ... ```)
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    # 2. Remove any leading prose lines before the diagram type keyword
    diagram_keywords = ("flowchart", "graph", "classDiagram", "sequenceDiagram",
                        "erDiagram", "gantt", "stateDiagram", "pie")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if any(line.strip().startswith(kw) for kw in diagram_keywords):
            text = "\n".join(lines[i:])
            break

    # 3. Remove double-quoted strings inside node label brackets
    #    e.g.  B{"USE_MOCK == \"1\""}  -->  B{USE_MOCK == 1}
    text = re.sub(r'"([^"]*)"', lambda m: m.group(1).replace('"', ''), text)

    # 4. Remove single-quoted strings inside node labels
    text = re.sub(r"'([^']*)'", lambda m: m.group(1), text)

    # 5. Strip stray backticks inside labels
    text = text.replace('`', '')

    return text.strip()
