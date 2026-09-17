from typing import Literal

from pydantic import BaseModel, Field


ColumnName = Literal[
    "category",
    "priority",
    "status",
    "agent_id",
    "ticket_id",
    "created_at",
    "resolution_time_hrs",
    "customer_rating",
]
MetricName = Literal["count", "avg_customer_rating", "avg_resolution_time_hrs"]
OperationName = Literal[
    "count",
    "group_count",
    "top_group",
    "lowest_avg_rating",
    "average",
    "highest_average_resolution",
    "filtered_tickets",
]


class QueryFilter(BaseModel):
    column: ColumnName
    operator: Literal["=", "!=", ">", ">=", "<", "<=", "is_null", "is_not_null", "not_within"] = "="
    value: str | float | int | None = None


class QueryPlan(BaseModel):
    operation: OperationName
    group_by: ColumnName | None = None
    metric: MetricName = "count"
    filters: list[QueryFilter] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=100)


class QueryResponse(BaseModel):
    question: str
    plan: QueryPlan
    answer: str
    results: list[dict]
