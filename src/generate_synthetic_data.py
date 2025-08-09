import os
import pandas as pd
import numpy as np
import random
import csv
from datetime import datetime, timedelta
from sklearn.datasets import make_classification

# Paths
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Parameters
N_SAMPLES = 1000      # number of synthetic transactions
N_FEATURES = 8        # additional engineered features
FRAUD_RATIO = 0.08    # 8% of transactions fraudulent

def generate_transactions():
    """
    Generate semi-realistic credit card transaction dataset.
    """
    np.random.seed(42)
    
    # Create synthetic classification data
    X, y = make_classification(
        n_samples=N_SAMPLES,
        n_features=N_FEATURES,
        n_informative=6,
        n_redundant=2,
        weights=[1 - FRAUD_RATIO, FRAUD_RATIO],
        random_state=42
    )
    
    df = pd.DataFrame(X, columns=[f"Feature{i}" for i in range(1, N_FEATURES+1)])
    
    # Add core transaction-like fields
    start_time = datetime.now() - timedelta(days=30)
    df['Time'] = [(start_time + timedelta(seconds=int(i * 200))).timestamp() for i in range(N_SAMPLES)]
    df['Amount'] = np.round(np.random.exponential(scale=80, size=N_SAMPLES), 2)
    df['UserID'] = np.random.randint(1000, 2000, size=N_SAMPLES)
    df['Lat'] = np.random.uniform(-90, 90, size=N_SAMPLES)
    df['Lon'] = np.random.uniform(-180, 180, size=N_SAMPLES)
    
    # Optional extra realistic patterns for fraud
    df.loc[y == 1, 'Amount'] *= np.random.uniform(1.5, 5.0, size=(y == 1).sum())
    df.loc[y == 1, 'Feature1'] *= np.random.uniform(2.0, 3.0, size=(y == 1).sum())
    
    return df, pd.Series(y, name="Class")

def save_train_files(X_df, y_series):
    # X_train_bal_adv.csv
    X_df.to_csv(os.path.join(DATA_DIR, "X_train_bal_adv.csv"), index=False)
    
    # y_train_bal_adv.csv
    y_series.to_csv(os.path.join(DATA_DIR, "y_train_bal_adv.csv"), index=False)
    
    print(f"[OK] Saved training data to {DATA_DIR}/")

def save_feedback_file(X_df, y_series):
    # Create small random feedback set (5 samples)
    fb_idx = np.random.choice(X_df.index, size=5, replace=False)
    features = X_df.loc[fb_idx].to_dict(orient="records")
    labels = y_series.loc[fb_idx].tolist()

    fb_path = os.path.join(DATA_DIR, "feedback_data.csv")
    with open(fb_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["features", "true_label"])
        for feat, lbl in zip(features, labels):
            writer.writerow([feat, lbl])
    print(f"[OK] Created fake feedback file at {fb_path}")

if __name__ == "__main__":
    X_df, y_series = generate_transactions()
    save_train_files(X_df, y_series)
    save_feedback_file(X_df, y_series)
    print("[DONE] Synthetic dataset generation complete.")
