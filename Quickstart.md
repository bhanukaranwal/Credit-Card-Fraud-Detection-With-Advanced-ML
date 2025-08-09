# 🚀 Quickstart — Credit Card Fraud Detection Platform

A short guide to get the full fraud detection stack up and running locally in minutes.

---

## 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- Git CLI
- Internet connection for pulling container images & installing Python deps

---

## 2. Clone the Repo

git clone https://github.com/yourname/credit-card-fraud-detection.git
cd credit-card-fraud-detection

--

---

## 3. Configure Environment

Copy `.env.example` (if present) or create `.env`:

cp .env.example .env

--

Edit `.env` and set values for:

API_TOKEN=supersecrettoken123
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/XXX/XXX
DATABASE_URL=postgresql://user:pass@db:5432/frauddb
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=frauddb
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your-grafana-api-key
PAGERDUTY_ROUTING_KEY=...
PAGERDUTY_API_KEY=...
SERVICENOW_INSTANCE=https://<your-instance>.service-now.com
SERVICENOW_USER=...
SERVICENOW_PASSWORD=...

--

For a quick local run, you can set dummy values for PagerDuty/ServiceNow integration if not using them.

---

## 4. Build & Launch

docker-compose up --build

--

This will start:

- **FastAPI API** (`http://localhost:8000/docs`)
- **Streamlit Dashboard** (`http://localhost:8501`)
- **Prometheus** (`http://localhost:9090`)
- **Grafana** (`http://localhost:3000`, user/pass: `admin`/`admin`)
- **PostgreSQL DB**
- **Scheduler** for nightly retrain + fairness audit
- **Incident Poller**
- **Kafka + Zookeeper** (optional, for streaming ingestion)

---

## 5. First Login

- Visit **Grafana** at `http://localhost:3000` and login (`admin` / `admin`), then change password.
- Navigate to **Dashboards → Fraud Detection Dashboards** to see live metrics.

---

## 6. Test Predictions

You can test the API directly:

curl -X POST "http://localhost:8000/predict"
-H "token: ${API_TOKEN}"
-H "Content-Type: application/json"
-d '{"Time":10,"Amount":100.5,"UserID":1234,"Lat":40.7128,"Lon":-74.0060,...}'

--

Or use **the Streamlit Dashboard** at `http://localhost:8501` → “Single Prediction” tab.

---

## 7. Try Core Features

- **Feedback Loop:** Submit analyst feedback in dashboard, retrain model nightly.
- **Compliance Reports:** Generate fairness/bias report PDF from dashboard.
- **Incident Monitor:** See real-time PagerDuty/ServiceNow incidents (requires credentials in `.env`).
- **Rollback Model:** From dashboard or API `/rollback_model`.

---

## 8. Shut Down

To stop and remove containers:

docker-compose down

--

---

**You’re ready!** For deeper config and architecture details, see [README.md](./README.md).
