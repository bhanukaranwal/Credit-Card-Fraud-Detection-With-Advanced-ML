import pandas as pd
from sqlalchemy import create_engine
import os
import requests
from src.notify import send_slack_alert, send_pagerduty_incident, create_grafana_annotation

DB_URL = os.getenv("DATABASE_URL")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GRAFANA_URL = os.getenv("GRAFANA_URL")

def run_audit():
    engine = create_engine(DB_URL)
    df = pd.read_sql("SELECT * FROM prediction_log", con=engine)
    protected_attrs = ["Gender", "Region"]
    results = []
    for attr in protected_attrs:
        if attr not in df.columns:
            df[attr] = df['features'].apply(lambda x: x.get(attr) if isinstance(x, dict) else None)
        if df[attr].nunique() > 1:
            group_stats = df.groupby(attr)['predicted_label'].mean()
            gap = group_stats.max() - group_stats.min()
            results.append((attr, gap))
            if gap > 0.05:
                send_slack_alert(f"⚠️ Fairness gap {gap:.2%} for {attr} exceeds threshold", "bias")
                send_pagerduty_incident(f"Bias gap breach: {attr} {gap:.2%}")
                create_grafana_annotation("GpK4WWlmz", 9, f"Bias gap alert: {attr} {gap:.2%}",
                                          f"{GRAFANA_URL}/d/GpK4WWlmz/fraud-detection-metrics?orgId=1&viewPanel=9")
    return results

if __name__ == "__main__":
    audit_results = run_audit()
    print("Audit Results:", audit_results)
