# 🛡️ Credit Card Fraud Detection Platform  
_A fully containerized, real-time, continuously learning fraud detection system with monitoring, compliance reporting, and incident management integration._

---

## 📖 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the System](#running-the-system)
- [Services](#services)
- [Dashboards & Monitoring](#dashboards--monitoring)
- [Data Flow](#data-flow)
- [Security](#security)
- [Extending the System](#extending-the-system)
- [License](#license)

---

## Overview

This platform provides **end-to-end credit card fraud detection** with:
- **FastAPI backend** for serving ML predictions, managing models, and streaming incident updates.
- **Continuously learning ML model** with automated retraining and drift detection.
- **PostgreSQL storage** for predictions, feedback, and compliance report archives.
- **Prometheus & Grafana** for live metrics and dashboard visualizations.
- **Slack, PagerDuty, ServiceNow integration** for real-time alerts and escalations.
- **Streamlit dashboard** for analysts with rich investigative & compliance tools.
- **Kafka** for optional high-throughput, real-time scoring.

---

## Features

- 🔍 **Fraud Prediction API** — real-time scoring for single/batch transactions.
- 📊 **Advanced Feature Engineering** — temporal, geospatial, profiling, anomaly features.
- 🤖 **Hybrid ML Model** — ensemble of tree models with meta learner.
- 🔄 **Automated Retraining** — scheduled & drift-triggered with zero downtime reload.
- 📈 **Prometheus Metrics** — fraud rate, retrains, fairness gaps, predictions.
- 📡 **Grafana Dashboards** — fraud trends, retraining history, bias monitoring.
- 🛠 **Incident Management** — Slack alerts with dashboard links, PagerDuty & ServiceNow escalation.
- 📜 **Compliance Reports** — on-demand fairness/bias PDF reports with SHAP plots.
- 🔴 **Real-Time Incident Feed** — live WebSocket updates in dashboard.
- 🗂 **Model Versioning & Rollback** — switch instantly between model versions.
- 💾 **Backups** — models, configs, DB dumps.

---

## Architecture

--
                  ┌───────────────────────────┐
                  │      Streamlit Dashboard   │
                  │  - Predictions/Feedback    │
                  │  - Compliance Reports      │
                  │  - Incident Monitor (WS)   │
                  └─────────────▲──────────────┘
                                │  WebSocket/REST
                                ▼
          ┌──────────────────────────────┐
          │          FastAPI API          │
          │ - Prediction endpoints        │
          │ - Model mgmt/versioning       │
          │ - WS incident broadcast       │
          │ - Metrics (/metrics)          │
          └─────────────┬────────────────┘
                        │
  ┌─────────────────────┼─────────────────────┐
  ▼                     ▼                     ▼
PostgreSQL DB Prometheus <──metrics── API Kafka Consumer
(Feedback, logs, ▲ (Optional stream scoring)
reports) │ scrape
│
Grafana <┘ dashboards

Scheduler Container:

Nightly retrain

Fairness audit → Alerts + Reports

Incident Poller:

Polls PagerDuty/ServiceNow

Broadcasts WS updates

--

---

## Technology Stack

- **Backend:** FastAPI, SQLAlchemy
- **Frontend:** Streamlit
- **Database:** PostgreSQL
- **ML:** Scikit-learn, XGBoost, Imbalanced-learn
- **Messaging:** Kafka (optional for streaming scoring)
- **Monitoring:** Prometheus + Grafana
- **Alerts/IM:** Slack, PagerDuty, ServiceNow
- **Orchestration:** Docker Compose
- **Task Scheduling:** supercronic in `scheduler` container

---

## Directory Structure

credit-card-fraud-detection/
├── docker-compose.yml
├── .env
├── requirements.txt
├── Dockerfile.api
├── Dockerfile.dashboard
├── Dockerfile.scheduler
├── Dockerfile.kafka_consumer
├── prometheus/
│ └── prometheus.yml
├── grafana/
│ ├── provisioning/
│ │ ├── dashboards/dashboard.yml
│ │ └── datasources/datasource.yml
│ └── dashboards/fraud_dashboard.json
├── scheduler.cron
├── src/
│ ├── api_service_advanced.py
│ ├── dashboard_investigator.py
│ ├── scheduled_retrainer.py
│ ├── incident_poller.py
│ ├── notify.py
│ ├── db.py
│ ├── feature_engineering_advanced.py
│ ├── model_training_hybrid.py
│ ├── kafka_stream_scoring.py
│ ├── fairness_audit.py
│ └── compliance_report.py
├── data/
│ └── ...
├── models/
│ └── ...
└── backup/

--

---

## Setup & Installation

1. **Clone the repo:**
git clone https://github.com/yourname/credit-card-fraud-detection.git
cd credit-card-fraud-detection

--

2. **Create `.env` file** with required secrets (see [Environment Variables](#environment-variables)).

3. **Build & Launch stack:**
docker-compose up --build

--

4. **Access services:**
- API: [http://localhost:8000/docs](http://localhost:8000/docs)
- Dashboard: [http://localhost:8501](http://localhost:8501)
- Grafana: [http://localhost:3000](http://localhost:3000) (admin/admin)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- PostgreSQL: localhost:5432

---

## Environment Variables

In `.env`:

API_TOKEN=supersecrettoken123
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXXX/XXXX/XXXX
DATABASE_URL=postgresql://user:pass@db:5432/frauddb
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=frauddb
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your-grafana-api-key
PAGERDUTY_ROUTING_KEY=your-pd-routing-key
PAGERDUTY_API_KEY=your-pd-api-key
SERVICENOW_INSTANCE=https://instance.service-now.com
SERVICENOW_USER=username
SERVICENOW_PASSWORD=password

--

---

## Running the System

**Start all services:**
docker-compose up --build

--

**Rebuild after changes:**
docker-compose up --build --force-recreate

--

---

## Services

| Service             | Description |
|----------------------|-------------|
| `api`               | FastAPI app with prediction endpoints, model mgmt, metrics, WS feed |
| `dashboard`         | Streamlit analyst dashboard |
| `scheduler`         | Nightly retraining + fairness audits |
| `incident_poller`   | Polls PagerDuty/ServiceNow and pushes live incidents |
| `kafka_consumer`    | Kafka-based real-time transaction scoring |
| `db`                | PostgreSQL for logs, feedback, reports |
| `prometheus`        | Metrics monitoring backend |
| `grafana`           | Metrics dashboards, annotations |
| `kafka` + `zookeeper` | Optional message broker for streaming |

---

## Dashboards & Monitoring

- **Fraud Metrics:** Fraud rate, flagged transaction count, prediction volume.
- **Model Retraining:** Count over time, annotations for version changes.
- **Fairness Monitoring:** Historical bias gaps for protected attributes.
- **Incident Management:** Integrated live incident view from PD/SN in dashboard.

---

## Data Flow

1. Transaction sent to API → features engineered → prediction returned.
2. Predictions + analyst feedback stored in Postgres.
3. Nightly scheduler:
   - Retrain model with feedback if drift detected.
   - Push retrain metrics + Slack/PagerDuty alerts + Grafana annotation.
4. Prometheus scrapes metrics from API, Grafana visualizes.
5. Incident poller pushes PD/SN changes via WS → dashboard updates instantly.
6. Compliance reports can be run on-demand from dashboard.

---

## Security

- API endpoints protected via token (`API_TOKEN`).
- Secrets in `.env`, never in source control.
- Grafana & Prometheus internal-only via Docker bridge (expose with auth if needed).
- Optional HTTPS + reverse proxy (nginx/Traefik).
- Postgres runs in isolated Docker network.

---

## Extending the System

You can easily:
- Add new ML models/feature engineering modules in `src/feature_engineering_advanced.py`.
- Add more metrics for Prometheus in API.
- Create additional Grafana dashboards and link them in `notify.py` for alerts.
- Integrate other IM tools via `notify.py`.
- Deploy to Kubernetes or cloud container services.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

**🚀 You now have a fully featured, production-ready fraud detection platform.**  
Monitor, detect, retrain, prove compliance, and act on incidents — all from one integrated system.
