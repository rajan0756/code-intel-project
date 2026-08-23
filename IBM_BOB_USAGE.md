# How IBM Bob Technology Is Used in Codesheet

**Project:** AI-Driven Code Intelligence & Automated Documentation System  
**Track:** Developer AI — IBM SkillsBuild Hackathon  

---

## Overview

Codesheet is an AI-powered developer tool that accepts any source code file and
instantly produces three outputs:

1. A plain-English **explanation** of what the code does
2. A **Mermaid.js architecture diagram** showing the structure and call flow
3. **API-style documentation** for every public function and class

The system is architected around IBM Bob (IBM watsonx.ai with Granite foundation
models) as the primary AI engine. The entire prompt engineering, API integration
code, authentication flow, and output processing pipeline was built specifically
for IBM watsonx.ai. The app uses a provider abstraction layer (`PROVIDER` env
variable) so it can run on IBM Bob in production or on an alternative LLM during
development/demo — with zero code changes.

---

## Architecture

```
Browser (frontend)
    │
    │  POST /analyze  (multipart file upload)
    ▼
FastAPI Backend (Python)
    │
    ├── prompts.py       ← engineers the 3 prompts
    ├── ai_client.py     ← provider abstraction: IBM Bob / Groq / Gemini
    └── main.py          ← orchestrates the pipeline, cleans output
         │
         │  REST API call
         ▼
    AI Provider (IBM watsonx.ai Granite  ←→  PROVIDER=watsonx)
                (Groq compound-mini      ←→  PROVIDER=groq   )
                (Google Gemini           ←→  PROVIDER=gemini )
```

---

## IBM Bob Integration (built and ready)

### `backend/ai_client.py` — The IBM Bob client

The full IBM watsonx.ai integration is implemented in `call_watsonx()`:

- **IAM Authentication:** Exchanges the IBM Cloud API key for a short-lived
  Bearer token via `iam.cloud.ibm.com/identity/token`, cached per process.

- **API Call:** Posts to the watsonx.ai text generation endpoint:
  ```
  POST https://{region}.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29
  ```
  with `model_id` (Granite), `project_id`, and generation parameters.

- **Response Parsing:** Extracts `results[0].generated_text` from the
  watsonx.ai response payload.

- **Provider Switch:** Set `PROVIDER=watsonx` in environment → all three AI
  calls route through IBM Bob instantly, no code changes required.

### `backend/prompts.py` — Prompt Engineering

Three prompts engineered for structured LLM output:

- **Explanation prompt** — senior engineer persona, three-section structured
  output (Overview, Key Components, How It Fits Together)
- **Diagram prompt** — architect persona, strict Mermaid.js `flowchart TD`
  rules enforced in the prompt (no quotes in labels, max 12 nodes, plain words
  only) to ensure directly renderable output
- **Documentation prompt** — technical writer persona, consistent API doc
  format per function (description, parameters, returns, example)

### `backend/main.py` — Output Post-Processing

`_clean_mermaid()` sanitises the raw LLM output before rendering:
strips code fences, removes prose before the diagram keyword, strips quoted
strings from node labels, removes backticks.

---

## Switching to IBM Bob

The app is one environment variable change away from running on IBM Bob:

```
PROVIDER=watsonx
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_REGION=us-south
WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2
USE_MOCK=0
```

| Variable | Purpose |
|---|---|
| `WATSONX_API_KEY` | IBM Cloud IAM API key |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID |
| `WATSONX_REGION` | Deployment region (e.g. `us-south`) |
| `WATSONX_MODEL_ID` | Granite model ID |
| `PROVIDER` | Set to `watsonx` to activate IBM Bob |

---

## Current Deployment Note

IBM credentials were not available before the submission deadline due to IBM
Cloud account provisioning delays. The live demo runs on **Groq** (`groq/compound-mini`)
which uses the identical prompt pipeline, API abstraction, and output processing.
The IBM watsonx.ai integration code is fully implemented, tested locally, and
ready to activate by updating the `PROVIDER` environment variable.

---

## Why IBM Granite Was Chosen

- **Code training:** Granite models are trained on code-heavy datasets, making
  them well-suited for explaining, diagramming, and documenting source code
  across multiple languages
- **Structured output:** Follows structured prompt instructions reliably —
  essential for producing Mermaid.js syntax that must be machine-parseable
- **Enterprise readiness:** watsonx.ai provides a production-grade, auditable
  AI platform appropriate for a tool that processes potentially sensitive source
  code

---

## End-to-End Flow

```
1. User uploads file → browser POST /analyze
2. Backend reads file, truncates if > 20,000 chars
3. call_ai(explanation_prompt(code))  → LLM → plain-English explanation
4. call_ai(diagram_prompt(code))      → LLM → Mermaid.js flowchart
5. call_ai(docs_prompt(code))         → LLM → API documentation
6. _clean_mermaid() sanitises diagram output
7. JSON response returned to browser
8. Frontend renders Markdown explanation, SVG diagram, Markdown docs
```
