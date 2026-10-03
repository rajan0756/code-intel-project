# Codesheet — AI-Driven Code Intelligence & Automated Documentation

Upload a source file → get a plain-English explanation, an auto-generated
architecture diagram (Mermaid.js), and API-style documentation, in one pass.

Built solo for the **SkillUp Hackathon × IBM SkillsBuild — Developer AI Track**.

🔗 **Live app:** https://code-intel-project.vercel.app
⚙️ **Backend API:** https://codeintel-backend-kn35.onrender.com/health

---

## What it does

Paste or upload a code file, and the app sends it to an LLM with three
separate prompts, returning:

1. **Explanation** — a plain-English overview of what the code does
2. **Diagram** — an auto-generated Mermaid.js architecture/flow diagram
3. **Documentation** — API-style docs for every public function and class

All three render in a single tabbed view, styled as a blueprint/schematic
sheet to match the "diagrams" theme of the tool itself.

## Project structure

```
code-intel-project/
├── backend/
│   ├── main.py           # FastAPI app, /analyze endpoint, CORS config
│   ├── prompts.py        # the 3 prompt templates sent to the LLM
│   ├── ai_client.py      # multi-provider LLM wrapper (Groq / Gemini / watsonx)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── index.html        # single-page UI, no build step, Mermaid.js rendering
└── render.yaml            # Render service definition
```

## AI provider support

`ai_client.py` is provider-agnostic. Set `PROVIDER` in your environment to
switch backends with no code changes:

| Provider | Env var | Get a key at |
|---|---|---|
| **Groq** (default) | `PROVIDER=groq` | console.groq.com |
| **Google Gemini** | `PROVIDER=gemini` | aistudio.google.com |
| **IBM watsonx.ai** | `PROVIDER=watsonx` | IBM Cloud / hackathon credentials |

Set `USE_MOCK=1` to skip all API calls and test the UI with placeholder
responses — useful for frontend work with no key configured.

The Groq model is itself configurable via `GROQ_MODEL`, since Groq
periodically deprecates models (this project has already migrated once,
see **Lessons learned** below).

## Running locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Minimum to get real output: set PROVIDER, the matching API key, and USE_MOCK=0
# Or leave USE_MOCK=1 to test the UI without any key at all

uvicorn main:app --reload --port 8000
```

Check it's running: open http://localhost:8000/health — you should see
`{"status": "ok"}`.

### Frontend

No build tools needed — it's a single HTML file. The frontend
auto-detects whether it's running locally or in production and points at
the right backend URL automatically.

```bash
cd frontend
python -m http.server 5500
```

Then open http://localhost:5500.

## Deployment

- **Backend** is deployed on [Render](https://render.com) (free tier) as a
  standard Web Service — root directory `backend`, build command
  `pip install -r requirements.txt`, start command
  `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- **Frontend** is deployed on [Vercel](https://vercel.com) as a static
  site — root directory `frontend`, no build step.
- CORS on the backend currently allows all origins (`*`) for simplicity;
  tighten this to the specific Vercel domain before any production use.

## Lessons learned / challenges overcome

Real issues hit while deploying this, kept here for anyone debugging
something similar:

- **401 Unauthorized** — backend was deployed with no environment
  variables set at all. Fixed by setting `PROVIDER`, `USE_MOCK`, and the
  provider API key on Render.
- **429 Too Many Requests** — each upload makes 3 sequential LLM calls,
  which exceeded Groq's free-tier tokens-per-minute cap on a large model.
  Fixed with a lighter model and retry logic with exponential backoff
  (10s → 20s → 30s) in `call_groq()`.
- **A CORS error that wasn't really a CORS error** — a crashed backend
  request (from the 401 above) showed up in the browser as a CORS
  failure, since a response with no body sends no CORS headers either.
  Traced to the real cause via Render's live logs, not by touching CORS
  config.
- **Model deprecation mid-project** — Groq decommissioned
  `groq/compound-mini` shortly after launch. `GROQ_MODEL` is now a
  configurable environment variable specifically so this doesn't require
  a code change next time.

## Roadmap / stretch goals

- [ ] Support a GitHub repo URL instead of single-file upload
- [ ] Multi-language-aware parsing (currently relies entirely on the LLM)
- [ ] "Copy as Markdown" button for generated docs
- [ ] Cache results per file hash so re-analysis is instant

## Known limitations

- Single file only, no repo-wide analysis yet
- Large files are truncated to keep prompts a reasonable size
- No auth — fine for a hackathon demo, not for production use
