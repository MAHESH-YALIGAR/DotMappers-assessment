from app.services.anomalies import detect_anomalies


def test_anomaly_detection_uses_latest_dataset_timestamp(session):
    result = detect_anomalies(session)
    assert result["reference_time"].isoformat() == "2024-03-30T18:06:00"
    assert len(result["rule_anomalies"]) == 80
    assert len(result["statistical_anomalies"]) == 21
    assert result["iqr_upper_bound"] == 48.15
