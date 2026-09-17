from datetime import timedelta

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Ticket


def detect_anomalies(session: Session) -> dict:
    tickets = list(session.scalars(select(Ticket).order_by(Ticket.created_at)))
    if not tickets:
        return {"reference_time": None, "rule_anomalies": [], "statistical_anomalies": [], "iqr_upper_bound": None}

    reference_time = max(ticket.created_at for ticket in tickets)
    age_cutoff = reference_time - timedelta(hours=24)
    rule_anomalies = [
        _ticket_dict(ticket)
        for ticket in tickets
        if ticket.priority in {"High", "Critical"}
        and ticket.status in {"Open", "Escalated"}
        and ticket.created_at < age_cutoff
    ]

    durations = pd.Series(
        [ticket.resolution_time_hrs for ticket in tickets if ticket.resolution_time_hrs is not None],
        dtype="float64",
    )
    if durations.empty:
        statistical_anomalies = []
        upper_bound = None
    else:
        q1 = float(durations.quantile(0.25))
        q3 = float(durations.quantile(0.75))
        upper_bound = q3 + 1.5 * (q3 - q1)
        statistical_anomalies = [
            _ticket_dict(ticket)
            for ticket in tickets
            if ticket.resolution_time_hrs is not None and ticket.resolution_time_hrs > upper_bound
        ]

    return {
        "reference_time": reference_time,
        "rule_anomalies": rule_anomalies,
        "statistical_anomalies": statistical_anomalies,
        "iqr_upper_bound": round(upper_bound, 2) if upper_bound is not None else None,
    }


def _ticket_dict(ticket: Ticket) -> dict:
    return {
        "ticket_id": ticket.ticket_id,
        "created_at": ticket.created_at.isoformat(),
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "resolution_time_hrs": ticket.resolution_time_hrs,
        "agent_id": ticket.agent_id,
        "customer_rating": ticket.customer_rating,
        "issue_summary": ticket.issue_summary,
    }
