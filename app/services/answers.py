from app.schemas.query import QueryPlan


def format_answer(plan: QueryPlan, results: list[dict]) -> str:
    if not results:
        return "No matching tickets found."
    if plan.operation == "count":
        return f"There are {results[0]['value']} matching tickets."
    if plan.operation == "average":
        return f"The average {plan.metric.replace('_', ' ')} is {results[0]['value']}."
    if plan.operation in {"top_group", "lowest_avg_rating", "highest_average_resolution", "group_count"}:
        first = results[0]
        return f"{first['group']} leads this result with {first['value']}."
    return f"Found {len(results)} matching tickets."
