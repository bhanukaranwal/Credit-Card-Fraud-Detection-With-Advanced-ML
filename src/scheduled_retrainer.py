import pandas as pd
import joblib
import os
import requests
from sqlalchemy.orm import Session
from src.db import SessionLocal, Feedback
from advanced_model_training import build_hybrid_model, find_best_threshold, feature_list
from src.notify import send_slack_alert, send_pagerduty_incident, create_grafana_annotation

MODEL_DIR = "models"
X_BASE = "data/X_train_bal_adv.csv"
Y_BASE = "data/y_train_bal_adv.csv"
CURRENT_VERSION_FILE = os.path.join(MODEL_DIR, "current_model_version.txt")

def get_current_version():
    try:
        with open(CURRENT_VERSION_FILE) as f:
            return int(f.read().strip())
    except:
        return 0

def detect_drift(X_base: pd.DataFrame, X_feedback: pd.DataFrame, threshold=0.1):
    # Simple drift check based on sample count or PSI can be implemented here
    if X_feedback.empty:
        return False
    # For brevity, just returning True for retrain if feedback present
    return True

def retrain():
    db = SessionLocal()
    X_base = pd.read_csv(X_BASE)
    y_base = pd.read_csv(Y_BASE)['Class']
    
    feedbacks = db.query(Feedback).all()
    if feedbacks:
        fb_dicts = [fb.features for fb in feedbacks]
        fb_y = [fb.true_label for fb in feedbacks]
        fb_X = pd.DataFrame(fb_dicts)
        fb_y = pd.Series(fb_y)
    else:
        fb_X = pd.DataFrame()
        fb_y = pd.Series()

    if not fb_X.empty and detect_drift(X_base, fb_X):
        X = pd.concat([X_base, fb_X], ignore_index=True)
        y = pd.concat([y_base, fb_y], ignore_index=True)
    else:
        X, y = X_base, y_base

    model = build_hybrid_model()
    model.fit(X, y)
    probs = model.predict_proba(X)[:, 1]
    best_t, _ = find_best_threshold(y, probs)

    new_version = get_current_version() + 1
    model_filepath = os.path.join(MODEL_DIR, f"stacked_fraud_model_v{new_version}.pkl")
    joblib.dump({'model': model, 'threshold': best_t}, model_filepath)

    with open(CURRENT_VERSION_FILE, 'w') as f:
        f.write(str(new_version))

    send_slack_alert(f"🤖 Model retrained to version {new_version} with threshold {best_t:.2f}", "retrain")
    send_pagerduty_incident(f"Fraud detection model retrained: version {new_version}", severity="info")
    create_grafana_annotation("GpK4WWlmz", 5, f"Model retrained v{new_version}", 
                              f"{os.getenv('GRAFANA_URL')}/d/GpK4WWlmz/retrain-dashboard?orgId=1&viewPanel=5")

    api_url = os.getenv("API_URL", "http://api:8000")
    api_token = os.getenv("API_TOKEN", "")
    if api_token:
        try:
            requests.post(f"{api_url}/model/reload", headers={"token": api_token}, timeout=10)
        except Exception as e:
            print(f"Error notifying API to reload model: {e}")

if __name__ == "__main__":
    retrain()
