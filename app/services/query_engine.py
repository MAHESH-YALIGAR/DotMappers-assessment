from collections.abc import Iterable

from sqlalchemy import Float, and_, cast, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Ticket
from app.schemas.query import QueryFilter, QueryPlan


COLUMN_MAP = {
    "category": Ticket.category,
    "priority": Ticket.priority,
    "status": Ticket.status,
    "agent_id": Ticket.agent_id,
    "ticket_id": Ticket.ticket_id,
    "created_at": Ticket.created_at,
    "resolution_time_hrs": Ticket.resolution_time_hrs,
    "customer_rating": Ticket.customer_rating,
}


def _filters(filters: Iterable[QueryFilter]):
    expressions = []
    for item in filters:
        column = COLUMN_MAP[item.column]
        if item.operator == "is_null":
            expressions.append(column.is_(None))
        elif item.operator == "is_not_null":
            expressions.append(column.is_not(None))
        elif item.operator == "not_within":
            expressions.append(or_(column.is_(None), column > item.value))
        elif item.operator in {">", ">=", "<", "<="}:
            expressions.append(getattr(column, {">": "__gt__", ">=": "__ge__", "<": "__lt__", "<=": "__le__"}[item.operator])(item.value))
        elif item.operator == "!=":
            expressions.append(column != item.value)
        else:
            expressions.append(column == item.value)
    return expressions


def _metric(metric: str):
    if metric == "avg_customer_rating":
        return func.avg(Ticket.customer_rating)
    if metric == "avg_resolution_time_hrs":
        return func.avg(Ticket.resolution_time_hrs)
    return func.count(Ticket.ticket_id)


def execute_plan(session: Session, plan: QueryPlan) -> list[dict]:
    conditions = _filters(plan.filters)
    metric_expression = _metric(plan.metric).label("value")

    if plan.operation == "filtered_tickets":
        statement = select(Ticket).where(*conditions).order_by(Ticket.created_at.desc()).limit(plan.limit)
        return [_ticket_dict(ticket) for ticket in session.scalars(statement)]

    if plan.operation == "count":
        statement = select(func.count(Ticket.ticket_id).label("value")).where(*conditions)
        return [{"value": session.execute(statement).scalar_one()}]

    if plan.operation == "average":
        statement = select(metric_expression).where(*conditions)
        value = session.execute(statement).scalar_one()
        return [{"value": round(float(value), 2) if value is not None else None}]

    group_column = COLUMN_MAP[plan.group_by or "category"]
    statement = select(group_column.label("group"), metric_expression).where(*conditions).group_by(group_column)
    if plan.operation in {"top_group", "highest_average_resolution"}:
        statement = statement.order_by(metric_expression.desc())
    elif plan.operation == "lowest_avg_rating":
        statement = statement.order_by(metric_expression.asc())
    else:
        statement = statement.order_by(metric_expression.desc())
    statement = statement.limit(plan.limit)
    return [{"group": row.group, "value": round(float(row.value), 2) if row.value is not None else None} for row in session.execute(statement)]


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
