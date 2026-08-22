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

IBM Bob (IBM watsonx.ai with Granite foundation models) is the AI engine that
powers all three outputs. Every analysis request sends the uploaded code to IBM
Bob with a carefully engineered prompt and renders the response directly in the
browser.

---

## Architecture

```
Browser (frontend)
    │
    │  POST /analyze  (multipart file upload)
    ▼
FastAPI Backend (Python)
    │
    ├── prompts.py       ← engineers the 3 prompts sent to IBM Bob
    ├── ai_client.py     ← sends prompts to IBM Bob, parses responses
    └── main.py          ← orchestrates the pipeline, cleans output
         │
         │  REST API call  (Bearer token auth)
         ▼
    IBM watsonx.ai — Granite foundation model
```

---

## Where IBM Bob Is Integrated

### 1. `backend/ai_client.py` — The IBM Bob client

This file handles all communication with IBM watsonx.ai:

- **IAM Authentication:** Exchanges the IBM Cloud API key for a short-lived
  Bearer token using IBM's IAM endpoint (`iam.cloud.ibm.com/identity/token`).
  The token is cached for the process lifetime to avoid redundant auth calls.

- **API Call:** Sends prompts to the watsonx.ai text generation endpoint:
  ```
  POST https://{region}.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29
  ```
  The request includes the `model_id` (IBM Granite), `project_id`, and
  generation parameters (`decoding_method: greedy`, `max_new_tokens: 1024`).

- **Response Parsing:** Extracts the generated text from
  `results[0].generated_text` in the watsonx.ai response payload.

- **Provider Abstraction:** The `call_ai()` function is the single entry point
  used throughout the app. Setting `PROVIDER=watsonx` in the environment routes
  all calls through IBM Bob. This design means the rest of the codebase never
  changes when switching providers.

### 2. `backend/prompts.py` — Prompt Engineering for IBM Bob

Three prompt templates are carefully engineered to get high-quality, structured
output from IBM Bob:

#### Explanation Prompt
Instructs IBM Bob to act as a senior software engineer and explain the uploaded
code in three structured sections: Overview, Key Components, and How It Fits
Together. The prompt explicitly asks for intent-focused explanation rather than
line-by-line restatement.

#### Diagram Prompt
Instructs IBM Bob to act as a software architect and produce a valid Mermaid.js
`flowchart TD` diagram. Strict rules are enforced in the prompt to ensure the
output is directly renderable: no quotes in node labels, maximum 12 nodes,
plain-word labels only, no subgraphs.

#### Documentation Prompt
Instructs IBM Bob to act as a technical writer and produce structured API
documentation for every public function and class, in a consistent format
covering description, parameters, return value, and a usage example.

### 3. `backend/main.py` — Output Post-Processing

The raw text IBM Bob returns is post-processed before being sent to the
frontend:

- **Mermaid cleaning:** The `_clean_mermaid()` function strips markdown code
  fences, removes any prose IBM Bob adds before the diagram keyword, strips
  quoted strings from node labels, and removes backticks — handling any minor
  deviations from the prompt instructions.

---

## IBM Bob Configuration

The IBM watsonx.ai connection is configured via environment variables:

| Variable | Purpose |
|---|---|
| `WATSONX_API_KEY` | IBM Cloud IAM API key |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID |
| `WATSONX_REGION` | Deployment region (e.g. `us-south`) |
| `WATSONX_MODEL_ID` | Granite model (e.g. `ibm/granite-13b-instruct-v2`) |
| `PROVIDER` | Set to `watsonx` to activate IBM Bob |

To switch to IBM Bob, update `backend/.env`:
```
PROVIDER=watsonx
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_REGION=us-south
WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2
USE_MOCK=0
```

---

## Why IBM Bob / IBM Granite

- **Code understanding:** IBM Granite models are specifically trained on
  code-heavy datasets, making them well-suited for explaining, diagramming, and
  documenting source code across multiple languages.

- **Structured output:** The models follow structured prompt instructions
  reliably, which is essential for producing Mermaid.js syntax that must be
  machine-parseable by the frontend renderer.

- **Enterprise readiness:** IBM watsonx.ai provides a production-grade,
  auditable AI platform — appropriate for a developer tooling product that
  processes potentially sensitive source code.

---

## Flow for a Single File Analysis

```
1. User uploads file → browser sends POST /analyze
2. Backend reads file, truncates if > 20,000 chars
3. call_ai(explanation_prompt(code))  → IBM Bob → plain-English explanation
4. call_ai(diagram_prompt(code))      → IBM Bob → Mermaid.js flowchart
5. call_ai(docs_prompt(code))         → IBM Bob → API documentation
6. _clean_mermaid() sanitises diagram output
7. JSON response sent to browser
8. Frontend renders: Markdown explanation, Mermaid diagram, Markdown docs
```

All three IBM Bob calls are made sequentially to respect rate limits and ensure
reliability during the hackathon demo.
