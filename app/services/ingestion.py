from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import Ticket


REQUIRED_COLUMNS = {
    "ticket_id",
    "created_at",
    "category",
    "priority",
    "status",
    "response_time_hrs",
    "resolution_time_hrs",
    "agent_id",
    "customer_rating",
    "issue_summary",
}


def load_csv(session: Session, csv_path: Path) -> int:
    dataframe = pd.read_csv(csv_path)
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f"CSV is missing required columns: {sorted(missing_columns)}")

    dataframe["created_at"] = pd.to_datetime(dataframe["created_at"], errors="raise")
    for column in ("response_time_hrs", "resolution_time_hrs", "customer_rating"):
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    dataframe = dataframe.where(pd.notna(dataframe), None)
    records = dataframe[list(REQUIRED_COLUMNS)].to_dict(orient="records")

    session.query(Ticket).delete()
    session.add_all([Ticket(**record) for record in records])
    session.commit()
    return len(records)
