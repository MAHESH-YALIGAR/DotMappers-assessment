from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    escalated_tickets: int
    resolved_tickets: int
    average_customer_rating: float | None
    average_resolution_time_hrs: float | None
