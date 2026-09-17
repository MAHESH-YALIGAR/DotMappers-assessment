# DOTMappers Support AI

AI-assisted support-ticket analysis for DOTMappers IT Pvt. Ltd. The app uses
Streamlit, FastAPI, SQLite, and optional Groq natural-language query planning.

## Run locally

Requires Python 3.10+.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.db.seed
```

Start the backend in one terminal:

```powershell
uvicorn app.main:app --reload
```

Start the UI in another activated terminal:

```powershell
streamlit run streamlit_app.py
```

Open:

- UI: <http://localhost:8501>
- API docs: <http://localhost:8000/docs>

## Groq (optional)

Add a new key to `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

The app works without a key using its offline fallback. Never commit `.env` or
a real API key.

## Features

- Ticket summaries and anomaly detection
- Natural-language support questions
- Validated, read-only SQL query plans
- Local CSV-to-SQLite data ingestion

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The test suite covers ingestion, queries, API responses, and anomaly detection.
