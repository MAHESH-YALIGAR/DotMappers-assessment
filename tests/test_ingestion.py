from datetime import datetime

from app.db.models import Ticket


def test_csv_is_loaded_with_typed_nullable_fields(session):
    ticket = session.get(Ticket, "TKT-005")
    assert ticket is not None
    assert isinstance(ticket.created_at, datetime)
    assert ticket.resolution_time_hrs is None
    assert ticket.customer_rating is None
