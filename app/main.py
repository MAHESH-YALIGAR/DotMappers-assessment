from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import SessionLocal, get_db, init_db
from app.db.models import Ticket
from app.schemas.anomaly import AnomalyResponse
from app.schemas.query import QueryResponse
from app.schemas.summary import SummaryResponse
from app.services.anomalies import detect_anomalies
from app.services.answers import format_answer
from app.services.ingestion import load_csv
from app.services.planner import QueryPlanner
from app.services.query_engine import execute_plan


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as session:
        if session.scalar(select(func.count(Ticket.ticket_id))) == 0:
            load_csv(session, settings.csv_path)
    yield


app = FastAPI(title="DOTMappers Support AI", version="1.0.0", lifespan=lifespan)
planner = QueryPlanner()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/summary", response_model=SummaryResponse)
def summary(session: Session = Depends(get_db)) -> SummaryResponse:
    total = session.scalar(select(func.count(Ticket.ticket_id))) or 0
    def count_status(status: str) -> int:
        return session.scalar(select(func.count(Ticket.ticket_id)).where(Ticket.status == status)) or 0
    return SummaryResponse(
        total_tickets=total,
        open_tickets=count_status("Open"),
        escalated_tickets=count_status("Escalated"),
        resolved_tickets=count_status("Resolved"),
        average_customer_rating=_rounded(session.scalar(select(func.avg(Ticket.customer_rating)))),
        average_resolution_time_hrs=_rounded(session.scalar(select(func.avg(Ticket.resolution_time_hrs)))),
    )


@app.post("/query", response_model=QueryResponse)
def query(question: str, session: Session = Depends(get_db)) -> QueryResponse:
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    plan = planner.plan(question)
    results = execute_plan(session, plan)
    return QueryResponse(question=question, plan=plan, answer=format_answer(plan, results), results=results)


@app.get("/anomalies", response_model=AnomalyResponse)
def anomalies(session: Session = Depends(get_db)) -> AnomalyResponse:
    return AnomalyResponse(**detect_anomalies(session))


def _rounded(value):
    return round(float(value), 2) if value is not None else None
