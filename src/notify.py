import os
import requests
from datetime import datetime

# Environment variables
SLACK_WEBHOOK_URL      = os.getenv("SLACK_WEBHOOK_URL")
GRAFANA_URL            = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_API_KEY        = os.getenv("GRAFANA_API_KEY")
PAGERDUTY_ROUTING_KEY  = os.getenv("PAGERDUTY_ROUTING_KEY")
PAGERDUTY_API_KEY      = os.getenv("PAGERDUTY_API_KEY")
SERVICENOW_INSTANCE    = os.getenv("SERVICENOW_INSTANCE")
SERVICENOW_USER        = os.getenv("SERVICENOW_USER")
SERVICENOW_PASSWORD    = os.getenv("SERVICENOW_PASSWORD")

# Pre-configured Grafana panel links
GRAFANA_LINKS = {
    "bias":        f"{GRAFANA_URL}/d/GpK4WWlmz/fraud-detection-metrics?orgId=1&viewPanel=9",
    "retrain":     f"{GRAFANA_URL}/d/GpK4WWlmz/retrain-dashboard?orgId=1&viewPanel=5",
    "fraud_spike": f"{GRAFANA_URL}/d/GpK4WWlmz/fraud-spike-dashboard?orgId=1&viewPanel=12",
}

def send_slack_alert(text, dashboard_key=None):
    if not SLACK_WEBHOOK_URL:
        return
    if dashboard_key:
        grafana_url = GRAFANA_LINKS.get(dashboard_key)
        if grafana_url:
            text += f"\nView dashboard: <{grafana_url}|Grafana Panel>"
    try:
        requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=5)
    except Exception as e:
        print(f"Slack alert failed: {e}")

def create_grafana_annotation(dashboard_uid, panel_id, text, link_url=None):
    if not GRAFANA_API_KEY:
        return
    url = f"{GRAFANA_URL}/api/annotations"
    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "dashboardUid": dashboard_uid,
        "panelId": panel_id,
        "time": int(datetime.utcnow().timestamp() * 1000),
        "text": text,
        "tags": ["fraud", "audit"],
        "isRegion": False
    }
    if link_url:
        payload["url"] = link_url
    try:
        requests.post(url, json=payload, headers=headers).raise_for_status()
    except Exception as e:
        print(f"Grafana annotation failed: {e}")

def send_pagerduty_incident(summary, severity="error"):
    if not PAGERDUTY_ROUTING_KEY:
        return
    payload = {
        "routing_key": PAGERDUTY_ROUTING_KEY,
        "event_action": "trigger",
        "payload": {
            "summary": summary,
            "severity": severity,
            "source": "fraud_detection_api"
        }
    }
    try:
        requests.post("https://events.pagerduty.com/v2/enqueue", json=payload).raise_for_status()
    except Exception as e:
        print(f"PagerDuty incident failed: {e}")

def create_servicenow_incident(short_description, description):
    if not SERVICENOW_INSTANCE:
        return
    url = f"{SERVICENOW_INSTANCE}/api/now/table/incident"
    auth = (SERVICENOW_USER, SERVICENOW_PASSWORD)
    payload = {
        "short_description": short_description,
        "description": description
    }
    try:
        r = requests.post(url, auth=auth, json=payload)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"ServiceNow incident creation failed: {e}")
