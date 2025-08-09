import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from fpdf import FPDF
import os
import requests
import asyncio
import json
import websockets

# Environment variables
DB_URL = os.getenv("DATABASE_URL")
API_TOKEN = os.getenv("API_TOKEN")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GRAFANA_URL = os.getenv("GRAFANA_URL")

# Grafana panel links
GRAFANA_LINKS = {
    "bias": f"{GRAFANA_URL}/d/GpK4WWlmz/fraud-detection-metrics?orgId=1&viewPanel=9",
    "retrain": f"{GRAFANA_URL}/d/GpK4WWlmz/retrain-dashboard?orgId=1&viewPanel=5",
    "fraud_spike": f"{GRAFANA_URL}/d/GpK4WWlmz/fraud-spike-dashboard?orgId=1&viewPanel=12"
}

def run_fairness_audit():
    engine = create_engine(DB_URL)
    df = pd.read_sql("SELECT * FROM prediction_log", con=engine)
    # Extract protected attributes
    protected_attrs = ["Gender", "Region"]
    results = []
    for attr in protected_attrs:
        if attr not in df.columns and df.shape[0] > 0:
            # Attempt to parse JSON features column for attr if needed
            df[attr] = df['features'].apply(lambda x: x.get(attr, None) if isinstance(x, dict) else None)
        if df[attr].nunique() > 1:
            group_stats = df.groupby(attr)['predicted_label'].mean()
            gap = group_stats.max() - group_stats.min()
            results.append((attr, gap))
    return results

def generate_compliance_report(shap_path, bias_report):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, "Fraud Detection Compliance Report", ln=True)
    if shap_path and os.path.exists(shap_path):
        pdf.image(shap_path, x=10, y=30, w=180)
    pdf.ln(85)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Fairness Audit Results:", ln=True)
    for attr, gap in bias_report:
        pdf.cell(200, 10, f"{attr} Gap: {gap:.2%}", ln=True)
    report_path = "compliance_report.pdf"
    pdf.output(report_path)
    return report_path

async def incident_ws_client():
    uri = f"ws://localhost:8000/ws/incidents"
    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            with st.container():
                st.write("### PagerDuty Incidents")
                for inc in data.get("pagerduty", []):
                    st.write(f"**{inc['id']}**: {inc['title']} (Status: {inc['status']})")
                st.write("### ServiceNow Incidents")
                for inc in data.get("servicenow", []):
                    st.write(f"**{inc['sys_id']}**: {inc['short_description']} (State: {inc['state']})")

menu = ["Single Prediction", "Batch Prediction", "Compliance & Fairness", "Incident Monitor"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Compliance & Fairness":
    st.header("Compliance & Fairness Audit")
    if st.button("Run Fairness Audit Now"):
        audit_results = run_fairness_audit()
        st.write("### Fairness Gaps")
        for attr, gap in audit_results:
            st.write(f"{attr}: {gap:.2%}")
            if gap > 0.05:
                st.warning(f"⚠️ Gap exceeds threshold!")
        report_file = generate_compliance_report("results/shap_summary.png", audit_results)
        with open(report_file, "rb") as f:
            st.download_button("Download Compliance Report (PDF)", f, file_name="compliance_report.pdf")

if choice == "Incident Monitor":
    st.header("Real-Time Incident Monitor")
    if st.button("Start Live Incident Feed"):
        asyncio.run(incident_ws_client())
