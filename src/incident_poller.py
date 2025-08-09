import asyncio
import requests
import os

API_URL = os.getenv("API_URL", "http://api:8000")
PD_API_KEY = os.getenv("PAGERDUTY_API_KEY")
SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE")
SERVICENOW_USER = os.getenv("SERVICENOW_USER")
SERVICENOW_PASS = os.getenv("SERVICENOW_PASSWORD")

def fetch_pagerduty_incidents():
    if not PD_API_KEY:
        return []
    url = "https://api.pagerduty.com/incidents"
    headers = {
        "Authorization": f"Token token={PD_API_KEY}",
        "Accept": "application/vnd.pagerduty+json;version=2"
    }
    params = {"statuses[]": "triggered", "limit": 10}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("incidents", [])
    except Exception as e:
        print(f"PagerDuty fetch error: {e}")
        return []

def fetch_servicenow_incidents():
    if not SERVICENOW_INSTANCE:
        return []
    url = f"{SERVICENOW_INSTANCE}/api/now/table/incident"
    params = {"sysparm_query": "state=1", "sysparm_limit": 10}
    try:
        response = requests.get(url, auth=(SERVICENOW_USER, SERVICENOW_PASS), params=params)
        response.raise_for_status()
        return response.json().get("result", [])
    except Exception as e:
        print(f"ServiceNow fetch error: {e}")
        return []

async def poll_and_push():
    previous_pd = []
    previous_sn = []
    while True:
        pd_incidents = fetch_pagerduty_incidents()
        sn_incidents = fetch_servicenow_incidents()
        if pd_incidents != previous_pd or sn_incidents != previous_sn:
            msg = {"pagerduty": pd_incidents, "servicenow": sn_incidents}
            try:
                requests.post(f"{API_URL}/broadcast_incident", json=msg, headers={"token": os.getenv("API_TOKEN")}, timeout=5)
            except Exception as e:
                print(f"Broadcast error: {e}")
            previous_pd = pd_incidents
            previous_sn = sn_incidents
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(poll_and_push())
