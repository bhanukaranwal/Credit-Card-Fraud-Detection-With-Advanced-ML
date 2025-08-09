from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect, Depends
import pandas as pd
import joblib
import os
from typing import List
from prometheus_client import Counter, Summary, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
import json
from sqlalchemy.orm import Session

from src.db import init_db, get_db, Feedback, PredictionLog
from src.notify import send_slack_alert, create_grafana_annotation, send_pagerduty_incident

app = FastAPI()
init_db()

# Prometheus instrumentation
instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)

PREDICTION_COUNT = Counter("fraud_predictions_total", "Total predictions made")
FRAUD_COUNT = Counter("fraud_flags_total", "Total fraud predictions")
AVG_PROB_SUMMARY = Summary("fraud_probability_summary", "Summary of fraud probabilities")
MODEL_RETRAIN_COUNT = Counter("fraud_model_retraining_total", "Number of times the model retrained")
FAIRNESS_GAPS = {
    "Gender": Gauge("fairness_gap_gender", "Fairness gap for Gender"),
    "Region": Gauge("fairness_gap_region", "Fairness gap for Region")
}

API_TOKEN = os.getenv("API_TOKEN")
MODEL_DIR = "models"
CURRENT_VERSION_FILE = os.path.join(MODEL_DIR, "current_model_version.txt")

# Model state
def get_current_version():
    try:
        with open(CURRENT_VERSION_FILE) as f:
            return int(f.read().strip())
    except:
        return None

def load_model(version: int):
    fp = os.path.join(MODEL_DIR, f"stacked_fraud_model_v{version}.pkl")
    if not os.path.exists(fp):
        raise FileNotFoundError
    return joblib.load(fp)

current_version = get_current_version()
model_info = load_model(current_version) if current_version else None
stacked_model, threshold = (model_info['model'], model_info['threshold']) if model_info else (None, None)

def verify_token(token: str):
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

# WebSocket handling
connected_clients = set()
@app.websocket("/ws/incidents")
async def websocket_incidents(ws: WebSocket):
    await ws.accept()
    connected_clients.add(ws)
    try:
        while True:
            await ws.receive_text()  # for keep-alive
    except WebSocketDisconnect:
        connected_clients.remove(ws)

async def broadcast_incidents(msg: dict):
    if not connected_clients:
        return
    data = json.dumps(msg)
    for client in list(connected_clients):
        try:
            await client.send_text(data)
        except:
            connected_clients.remove(client)

# API endpoints
@app.post("/predict")
def predict(transaction: dict, token: str = Header(...), db: Session = Depends(get_db)):
    verify_token(token)
    X = pd.DataFrame([transaction])
    prob = stacked_model.predict_proba(X)[0, 1]
    pred = int(prob >= threshold)
    db.add(PredictionLog(features=transaction, predicted_label=pred, predicted_prob=prob))
    db.commit()
    PREDICTION_COUNT.inc()
    AVG_PROB_SUMMARY.observe(prob)
    if pred == 1:
        FRAUD_COUNT.inc()
    if prob > 0.9:
        send_slack_alert(f"🚨 Fraud Alert: {prob:.2%}", "fraud_spike")
    return {"fraud_prediction": pred, "fraud_probability": float(prob), "threshold": float(threshold)}

@app.post("/feedback")
def feedback(items: List[dict], token: str = Header(...), db: Session = Depends(get_db)):
    verify_token(token)
    for fb in items:
        db.add(Feedback(features=fb['features'], true_label=fb['analyst_label']))
    db.commit()
    return {"status": "feedback_saved", "new_records": len(items)}

@app.post("/retrain")
def retrain_model(token: str = Header(...)):
    verify_token(token)
    # Simplified retrain logic (see scheduled retrainer for full)
    send_slack_alert("🤖 Manual retrain triggered", "retrain")
    MODEL_RETRAIN_COUNT.inc()
    return {"status": "ok"}

@app.post("/rollback_model")
def rollback(v: int, token: str = Header(...)):
    verify_token(token)
    global stacked_model, threshold, current_version
    model_info = load_model(v)
    stacked_model, threshold = model_info['model'], model_info['threshold']
    current_version = v
    with open(CURRENT_VERSION_FILE, 'w') as f:
        f.write(str(v))
    return {"status": "rolled_back", "version": v}

@app.post("/model/reload")
def reload_model(token: str = Header(...)):
    verify_token(token)
    global stacked_model, threshold, current_version
    current_version = get_current_version()
    model_info = load_model(current_version)
    stacked_model, threshold = model_info['model'], model_info['threshold']
    return {"status": "reloaded", "version": current_version}

@app.post("/broadcast_incident")
async def broadcast_incident(msg: dict, token: str = Header(...)):
    verify_token(token)
    await broadcast_incidents(msg)
    return {"status": "broadcasted"}
