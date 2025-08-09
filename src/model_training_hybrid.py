from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

def build_hybrid_model():
    base_learners = [
        ('rf', RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)),
        ('xgb', XGBClassifier(n_estimators=200, scale_pos_weight=1, eval_metric='logloss', use_label_encoder=False))
    ]
    meta = LogisticRegression(max_iter=1000, class_weight='balanced')
    ensemble_model = StackingClassifier(
        estimators=base_learners,
        final_estimator=meta,
        passthrough=True,
        n_jobs=-1
    )
    return ensemble_model
