# DOTMappers Support AI

An AI-assisted customer-support ticket assessment project for DOTMappers IT Pvt. Ltd. It loads the provided read-only CSV into SQLite, uses Groq to translate natural language into a validated query plan, and executes the calculation with SQLAlchemy. The LLM never executes SQL.

## Architecture

```text
Streamlit -> FastAPI -> Groq query planner -> Pydantic QueryPlan -> SQLAlchemy/SQLite -> exact result
```

The planner uses a deterministic fallback when `GROQ_API_KEY` is absent, so the API and tests work offline.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.db.seed
```

Set `GROQ_API_KEY` in `.env` to enable Groq planning. Do not commit `.env`; it is ignored by git. The loader prefers `data/support_tickets.csv` and also supports the supplied root-level `support_tickets.csv` without modifying it.

## Run

Terminal 1:

```powershell
uvicorn app.main:app --reload
```

Terminal 2:

```powershell
streamlit run streamlit_app.py
```

Open the Streamlit URL shown by the command. FastAPI docs are available at `http://localhost:8000/docs`.

## Run with Docker Compose

Docker avoids local Python and pip environment issues. Install Docker Desktop, then run from the project folder:

```powershell
Copy-Item .env.example .env
# Add a new GROQ_API_KEY to .env, or leave the placeholder for offline fallback
docker compose up --build
```

Open the UI at `http://localhost:8501` and FastAPI at `http://localhost:8000/docs`. Stop the services with `Ctrl+C`; remove the containers with `docker compose down`. SQLite data is stored in the `ticket_database` Docker volume.

## API

- `GET /health`: liveness check.
- `GET /summary`: ticket counts and averages.
- `POST /query?question=...`: returns the validated plan, exact SQL-backed results, and a short answer.
- `GET /anomalies`: returns rule and IQR anomalies.

Example questions:

- `How many tickets are currently open?`
- `How many critical tickets are unresolved?`
- `Which agent resolved the most tickets?`
- `Which agent has the lowest average customer rating?`
- `What is the average customer rating for Technical tickets?`
- `Show Critical tickets not resolved within 12 hours.`
- `Which category has the highest average resolution time?`

## Anomaly detection

Rule anomalies are High/Critical tickets with Open/Escalated status older than 24 hours. The age reference is the latest `created_at` in the dataset, making historical results reproducible. Statistical anomalies use the upper IQR fence: `Q3 + 1.5 * (Q3 - Q1)` for non-null `resolution_time_hrs` values. No ML model is trained.

## Technology choices and security

Python, FastAPI, Streamlit, SQLite, SQLAlchemy, pandas, Groq, Pydantic, pytest, and python-dotenv are used directly. Query plans validate operations, columns, metrics, operators, and limits with Pydantic. SQLAlchemy builds only allowlisted SELECT-style reads; the LLM cannot submit arbitrary SQL. API keys are read from `.env` and never returned by the API.

## Tests

```powershell
pytest -q
```

The tests cover CSV type/null ingestion, query planning and SQL results, and both anomaly methods. Values in this README intentionally do not reproduce dataset results; run the API or tests to calculate current results from the provided file.

## Limitations

The query language is intentionally narrow and optimized for the assessment examples. Groq availability, model behavior, and network access can affect natural-language planning; the deterministic fallback keeps core behavior usable offline. SQLite is appropriate for this assessment and small support datasets, but a production deployment would need operational database and authentication decisions.
