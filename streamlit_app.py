import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="DOTMappers Support AI", page_icon="🎫", layout="wide")
st.title("DOTMappers Support AI")
st.caption("Ask questions about support operations using a validated SQL-backed query plan.")

try:
    summary = requests.get(f"{API_URL}/summary", timeout=5).json()
    cols = st.columns(6)
    for column, (label, key) in zip(cols, [
        ("Total", "total_tickets"), ("Open", "open_tickets"), ("Escalated", "escalated_tickets"),
        ("Resolved", "resolved_tickets"), ("Avg rating", "average_customer_rating"), ("Avg resolution hrs", "average_resolution_time_hrs"),
    ]):
        column.metric(label, summary[key])
except requests.RequestException:
    st.error("API is unavailable. Start FastAPI with: uvicorn app.main:app --reload")

st.subheader("Ask the ticket database")
question = st.text_input("Natural-language question", placeholder="Which agent resolved the most tickets?")
if st.button("Ask", type="primary") and question:
    try:
        response = requests.post(f"{API_URL}/query", params={"question": question}, timeout=30)
        response.raise_for_status()
        payload = response.json()
        st.success(payload["answer"])
        with st.expander("Validated query plan"):
            st.json(payload["plan"])
        st.dataframe(payload["results"], use_container_width=True)
    except requests.RequestException as error:
        st.error(f"Query failed: {error}")

st.subheader("Anomalies")
if st.button("Refresh anomalies"):
    try:
        anomaly_response = requests.get(f"{API_URL}/anomalies", timeout=10)
        anomaly_response.raise_for_status()
        anomaly_data = anomaly_response.json()
        st.write(f"Reference time: {anomaly_data['reference_time']}")
        st.write(f"IQR upper bound: {anomaly_data['iqr_upper_bound']}")
        st.write("Rule anomalies")
        st.dataframe(anomaly_data["rule_anomalies"], use_container_width=True)
        st.write("Statistical anomalies")
        st.dataframe(anomaly_data["statistical_anomalies"], use_container_width=True)
    except requests.RequestException as error:
        st.error(f"Anomaly request failed: {error}")
