# Codesheet — AI-Driven Code Intelligence & Automated Documentation

Upload a source file → get a plain-English explanation, an auto-generated
architecture diagram (Mermaid.js), and API-style documentation, all powered
by IBM Bob.

Built for the **SkillUp Hackathon × IBM SkillsBuild — Developer AI Track**.

## Project structure

```
code-intel-project/
├── backend/
│   ├── main.py           # FastAPI app, /analyze endpoint
│   ├── prompts.py        # the 3 prompt templates sent to IBM Bob
│   ├── ai_client.py       # IBM Bob API wrapper (fill in your credentials)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html         # single-page UI (no build step needed)
```

## 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env — for now just leave USE_MOCK=1 so you can test without IBM Bob credentials yet

uvicorn main:app --reload --port 8000
```

Check it's running: open http://localhost:8000/health — you should see `{"status": "ok"}`.

## 2. Frontend setup

No build tools needed — it's a single HTML file.

```bash
cd frontend
python -m http.server 5500
```

Then open http://localhost:5500 in your browser.

(Or just double-click `index.html` to open it directly — CORS is already
open on the backend for the hackathon demo.)

## 3. Wiring up IBM Bob

Right now `ai_client.py` has placeholder logic for calling IBM Bob, since the
exact endpoint/auth format depends on what SkillUp/IBM SkillsBuild gives you
for this hackathon. Once you have those docs:

1. Open `backend/ai_client.py`
2. Fill in `IBM_BOB_ENDPOINT` and `IBM_BOB_API_KEY` in your `.env` file
3. Adjust the request payload and response parsing inside `call_ibm_bob()` to
   match IBM Bob's actual API contract (look for the `# TODO` comments)
4. Set `USE_MOCK=0` in `.env`

Until then, `USE_MOCK=1` lets you build and test the full upload → tabs → 
diagram flow with fake responses, so you're not blocked.

## 4. Testing it

Try uploading a real file from one of your own projects — something with
2-4 functions or a small class is the sweet spot for a demo (big enough to
be interesting, small enough that the output is easy to read on stage).

## Roadmap / stretch goals (if you have extra time)

- [ ] Support a GitHub repo URL instead of single-file upload (fetch + loop over files)
- [ ] Multi-language parsing awareness (currently language-agnostic, relies on the LLM)
- [ ] "Copy as Markdown" button for the generated docs
- [ ] Cache results per file hash so re-analyzing the same file is instant

## Known limitations (be upfront about these in your demo)

- Single file only, no repo-wide analysis yet
- Files are truncated at ~20k characters to keep prompts a reasonable size
- No auth — fine for a hackathon demo, not for production
