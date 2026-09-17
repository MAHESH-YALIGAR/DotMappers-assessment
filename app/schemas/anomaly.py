from datetime import datetime

from pydantic import BaseModel


class AnomalyResponse(BaseModel):
    reference_time: datetime
    rule_anomalies: list[dict]
    statistical_anomalies: list[dict]
    iqr_upper_bound: float | None
