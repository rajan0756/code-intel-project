"""
AI client — supports IBM watsonx.ai, Groq, and Google Gemini.

Set PROVIDER in your .env to switch between them:
  PROVIDER=groq      → free, no card, get key at console.groq.com
  PROVIDER=gemini    → free tier, no card, get key at aistudio.google.com
  PROVIDER=watsonx   → IBM watsonx.ai (hackathon credentials)

USE_MOCK=1 skips all API calls for local UI testing.
"""

import os
import requests

PROVIDER = os.environ.get("PROVIDER", "groq").lower()

# ── Groq ─────────────────────────────────────────────────────────────────────
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL    = os.environ.get("GROQ_MODEL", "groq/compound-mini")

# ── Gemini ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# ── IBM watsonx.ai ────────────────────────────────────────────────────────────
WATSONX_API_KEY    = os.environ.get("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID", "")
WATSONX_REGION     = os.environ.get("WATSONX_REGION", "us-south")
WATSONX_MODEL_ID   = os.environ.get("WATSONX_MODEL_ID", "ibm/granite-13b-instruct-v2")

_IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
_cached_iam_token: str | None = None


# ── Provider implementations ──────────────────────────────────────────────────

def call_groq(prompt: str) -> str:
    import time
    for attempt in range(3):
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024,
                "temperature": 0.2,
            },
            timeout=60,
        )
        if resp.status_code == 429:
            wait = 10 * (attempt + 1)  # 10s, 20s, 30s
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    resp.raise_for_status()  # raise after all retries exhausted


def call_gemini(prompt: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    resp = requests.post(
        url,
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def _get_iam_token() -> str:
    global _cached_iam_token
    if _cached_iam_token:
        return _cached_iam_token
    resp = requests.post(
        _IAM_TOKEN_URL,
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": WATSONX_API_KEY,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    _cached_iam_token = resp.json()["access_token"]
    return _cached_iam_token


def call_watsonx(prompt: str) -> str:
    token = _get_iam_token()
    url = f"https://{WATSONX_REGION}.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "model_id": WATSONX_MODEL_ID,
            "input": prompt,
            "project_id": WATSONX_PROJECT_ID,
            "parameters": {"decoding_method": "greedy", "max_new_tokens": 1024},
        },
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["results"][0]["generated_text"].strip()


# ── Entry point ───────────────────────────────────────────────────────────────

def call_ai(prompt: str) -> str:
    if os.environ.get("USE_MOCK") == "1":
        return _mock_response(prompt)
    if PROVIDER == "gemini":
        return call_gemini(prompt)
    if PROVIDER == "watsonx":
        return call_watsonx(prompt)
    return call_groq(prompt)  # default


def _mock_response(prompt: str) -> str:
    if "Mermaid" in prompt:
        return "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]"
    if "documentation" in prompt.lower():
        return "### `example_function(x)`\n**Description:** Example placeholder doc.\n**Parameters:** x (int) — input value\n**Returns:** int — result"
    return "**Overview**\nMock explanation — set USE_MOCK=0 and configure a provider to get real output.\n\n**Key components**\n- Placeholder"
