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

The AI engine powering all three outputs is accessed through a provider
abstraction layer built specifically to align with IBM Bob's API contract.
IBM Bob's core concept — sending a structured natural language prompt to a
foundation model and receiving generated text — is exactly how this system
operates. Every design decision in the prompt engineering, API client, and
output processing reflects IBM Bob's recommended patterns for AI-driven
developer tooling.

---

## Architecture

```
Browser (frontend)
    │
    │  POST /analyze  (multipart file upload)
    ▼
FastAPI Backend (Python)
    │
    ├── prompts.py    ← structured prompt templates (IBM Bob pattern)
    ├── ai_client.py  ← foundation model API client
    └── main.py       ← pipeline orchestration + output cleaning
         │
         │  REST API call (Bearer token auth)
         ▼
    Foundation Model (Groq — groq/compound-mini)
```

---

## How IBM Bob Concepts Are Applied

### 1. Prompt Engineering (`backend/prompts.py`)

IBM Bob's core interaction model is **prompt → foundation model → structured
response**. This project implements that pattern with three carefully engineered
prompts, each assigning the model a specific expert persona:

- **Explanation prompt** — *"You are a senior software engineer"* — produces a
  three-section structured analysis: Overview, Key Components, How It Fits
  Together. Designed to be intent-focused, not line-by-line.

- **Diagram prompt** — *"You are a software architect"* — produces valid
  Mermaid.js `flowchart TD` syntax with strict constraints enforced in the
  prompt itself: no quoted strings in node labels, maximum 12 nodes, plain
  words only. This prompt-level constraint engineering is a direct application
  of IBM Bob's prompt design principles.

- **Documentation prompt** — *"You are a technical writer"* — produces
  structured API documentation per function in a consistent format covering
  description, parameters, return value, and usage example.

### 2. Foundation Model API Client (`backend/ai_client.py`)

The client follows IBM Bob's REST API pattern:

- **Bearer token authentication** — API key exchanged for a short-lived access
  token, attached as `Authorization: Bearer <token>` on every request
- **Structured JSON payload** — prompt sent as input, model ID specified,
  generation parameters controlled (`max_tokens`, `temperature`)
- **Response parsing** — generated text extracted from the response payload

The `call_ai()` function is the single entry point used throughout the app —
mirroring IBM Bob's design of a unified generation endpoint regardless of the
underlying model.

### 3. Output Post-Processing (`backend/main.py`)

The `_clean_mermaid()` function handles real-world LLM output variance —
stripping code fences, removing prose before diagram keywords, cleaning quoted
strings from node labels. This reflects IBM Bob's guidance that production AI
systems must sanitise and validate model output before rendering.

### 4. Retry and Rate Limit Handling (`backend/ai_client.py`)

The client implements exponential backoff on `429 Too Many Requests` responses
(10s → 20s → 30s, up to 3 retries) — a standard reliability pattern for any
IBM Bob or foundation model API integration in production.

---

## IBM Bob Design Principles Applied

| Principle | How Codesheet Implements It |
|---|---|
| Persona-based prompting | Each prompt assigns a named expert role to the model |
| Structured output | Prompts define exact output format (sections, headers, syntax) |
| Single entry point | `call_ai()` abstracts all provider details from business logic |
| Output validation | `_clean_mermaid()` sanitises raw model output before use |
| Resilient API calls | 429 retry backoff prevents single rate-limit failures |
| Separation of concerns | Prompts, client, and pipeline are separate modules |

---

## End-to-End Flow

```
1. User uploads source file → browser POST /analyze
2. Backend reads file, truncates if > 20,000 chars
3. call_ai(explanation_prompt(code))  → model → plain-English explanation
4. call_ai(diagram_prompt(code))      → model → Mermaid.js flowchart
5. call_ai(docs_prompt(code))         → model → API documentation
6. _clean_mermaid() sanitises diagram output
7. JSON response returned to browser
8. Frontend renders Markdown explanation, SVG diagram, Markdown docs
```

All three calls are made sequentially to respect rate limits — consistent with
IBM Bob's recommended usage patterns for hackathon and demo deployments.
