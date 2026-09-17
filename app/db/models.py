from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    response_time_hrs: Mapped[float | None] = mapped_column(Float, nullable=True)
    resolution_time_hrs: Mapped[float | None] = mapped_column(Float, nullable=True)
    agent_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    customer_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    issue_summary: Mapped[str] = mapped_column(Text, nullable=False)
