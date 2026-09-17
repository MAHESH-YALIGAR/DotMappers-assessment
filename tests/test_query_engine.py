from app.services.planner import QueryPlanner
from app.services.query_engine import execute_plan


def test_open_ticket_count_uses_sql(session):
    plan = QueryPlanner().plan("How many tickets are currently open?")
    assert plan.filters[0].value == "Open"
    assert execute_plan(session, plan) == [{"value": 111}]


def test_agent_ranking_is_computed_by_sql(session):
    plan = QueryPlanner().plan("Which agent resolved the most tickets?")
    results = execute_plan(session, plan)
    assert results[0] == {"group": "AGT-12", "value": 37.0}


def test_rating_filter_and_average(session):
    plan = QueryPlanner().plan("What is the average customer rating for Technical tickets?")
    assert execute_plan(session, plan) == [{"value": 3.74}]
