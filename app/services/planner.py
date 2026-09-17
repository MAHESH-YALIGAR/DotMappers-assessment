import json
import re

from app.config import settings
from app.schemas.query import QueryPlan


SYSTEM_PROMPT = """You create JSON query plans for a support ticket database. Never write SQL.
Allowed operations: count, group_count, top_group, lowest_avg_rating, average, highest_average_resolution, filtered_tickets.
Allowed columns: category, priority, status, agent_id, ticket_id, created_at, resolution_time_hrs, customer_rating.
Allowed metrics: count, avg_customer_rating, avg_resolution_time_hrs.
Filters use operators =, !=, >, >=, <, <=, is_null, is_not_null, not_within. Return only valid JSON with keys operation, group_by, metric, filters, limit.
"""


class QueryPlanner:
    def plan(self, question: str) -> QueryPlan:
        if settings.groq_api_key:
            try:
                return self._groq_plan(question)
            except Exception:
                pass
        return self._fallback_plan(question)

    def _groq_plan(self, question: str) -> QueryPlan:
        from groq import Groq

        response = Groq(api_key=settings.groq_api_key).chat.completions.create(
            model=settings.groq_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
        )
        payload = json.loads(response.choices[0].message.content)
        return QueryPlan.model_validate(payload)

    def _fallback_plan(self, question: str) -> QueryPlan:
        text = question.lower()
        filters = []
        category_match = re.search(r"for\s+(general|billing|technical|account|access|product)\s+tickets?", text)
        if category_match:
            filters.append({"column": "category", "operator": "=", "value": category_match.group(1).capitalize()})
        for column in ("priority", "status"):
            match = re.search(rf"{column}\s+(?:tickets?\s+)?(?:that are\s+|with\s+)?(?:=\s*)?([a-z]+)", text)
            if match:
                filters.append({"column": column, "operator": "=", "value": match.group(1).capitalize()})
        if "critical" in text:
            filters.append({"column": "priority", "operator": "=", "value": "Critical"})
        if "open" in text and "unresolved" not in text:
            filters.append({"column": "status", "operator": "=", "value": "Open"})
        elif "unresolved" in text:
            filters.append({"column": "status", "operator": "!=", "value": "Resolved"})
        if "not resolved" in text and "within" in text:
            hours = re.search(r"within\s+(\d+(?:\.\d+)?)\s+hours?", text)
            if hours:
                filters.append({"column": "resolution_time_hrs", "operator": "not_within", "value": float(hours.group(1))})
        if "how many" in text or "count" in text:
            return QueryPlan(operation="count", filters=filters)
        if "lowest average customer rating" in text:
            return QueryPlan(operation="lowest_avg_rating", group_by="agent_id", metric="avg_customer_rating", filters=filters)
        if "resolved the most" in text or "most tickets" in text:
            return QueryPlan(operation="top_group", group_by="agent_id", metric="count", filters=[*filters, {"column": "status", "operator": "=", "value": "Resolved"}])
        if "highest average resolution" in text:
            return QueryPlan(operation="highest_average_resolution", group_by="category", metric="avg_resolution_time_hrs", filters=filters)
        if "average customer rating" in text:
            return QueryPlan(operation="average", metric="avg_customer_rating", filters=filters)
        return QueryPlan(operation="filtered_tickets", filters=filters)
