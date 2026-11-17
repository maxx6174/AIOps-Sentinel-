import json
from datetime import datetime
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from app.config import (
    FEATURE_COLUMNS,
    SYNTHETIC_DATASET_PATH,
    ISOLATION_FOREST_PATH,
    RANDOM_FOREST_PATH,
    LOGISTIC_REGRESSION_PATH,
    SCALER_PATH,
    METRICS_REPORT_PATH
)
from app.ml.dataset_generator import save_default_datasets

def train_and_evaluate_all(seed: int = 42):
    """
    Executes end-to-end model training, comparative evaluation, and persistence.
    1. Preprocesses synthetic telemetry with strict leakage prevention.
    2. Trains Isolation Forest for unsupervised anomaly detection.
    3. Trains Random Forest Classifier for supervised failure prediction.
    4. Trains Logistic Regression as standard baseline.
    5. Computes realistic comparative metrics (Accuracy, Precision, Recall, F1, ROC-AUC).
    6. Persists artifacts and structured evaluation report.
    """
    # Force re-generation with updated realistic distribution
    save_default_datasets()

    df = pd.read_csv(SYNTHETIC_DATASET_PATH)

    X = df[FEATURE_COLUMNS].values
    y = df["failure_occurred"].values
    y_anomaly = df["is_anomaly"].values

    # Train / test split with stratification to prevent target imbalance leakage
    X_train, X_test, y_train, y_test, _, y_anomaly_test = train_test_split(
        X, y, y_anomaly, test_size=0.25, random_state=seed, stratify=y
    )

    # Standard scaling with strict train-only fit
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Isolation Forest (Unsupervised Anomaly Detection)
    # Contamination ~0.20 reflects true anomalous fraction
    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=0.20,
        max_samples="auto",
        random_state=seed
    )
    iso_forest.fit(X_train_scaled)

    # Isolation Forest outputs: -1 for anomaly, 1 for inlier
    iso_preds_raw = iso_forest.predict(X_test_scaled)
    iso_preds = np.where(iso_preds_raw == -1, 1, 0)
    iso_scores = -iso_forest.score_samples(X_test_scaled)  # higher = more anomalous

    iso_metrics = {
        "model_name": "Isolation Forest",
        "model_type": "Unsupervised Anomaly Detection",
        "accuracy": round(float(accuracy_score(y_anomaly_test, iso_preds)), 4),
        "precision": round(float(precision_score(y_anomaly_test, iso_preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_anomaly_test, iso_preds, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_anomaly_test, iso_preds, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_anomaly_test, iso_scores)), 4),
        "confusion_matrix": confusion_matrix(y_anomaly_test, iso_preds).tolist(),
        "feature_importances": None
    }

    # 2. Random Forest Classifier (Primary Failure Prediction Model)
    rf_clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=9,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=seed
    )
    rf_clf.fit(X_train_scaled, y_train)

    rf_preds = rf_clf.predict(X_test_scaled)
    rf_probs = rf_clf.predict_proba(X_test_scaled)[:, 1]

    rf_importances = dict(zip(FEATURE_COLUMNS, [round(float(v), 4) for v in rf_clf.feature_importances_]))

    rf_metrics = {
        "model_name": "Random Forest Classifier",
        "model_type": "Ensemble Supervised Classifier (Primary)",
        "accuracy": round(float(accuracy_score(y_test, rf_preds)), 4),
        "precision": round(float(precision_score(y_test, rf_preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, rf_preds, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, rf_preds, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, rf_probs)), 4),
        "confusion_matrix": confusion_matrix(y_test, rf_preds).tolist(),
        "feature_importances": rf_importances
    }

    # 3. Logistic Regression (Baseline Comparison Model)
    lr_clf = LogisticRegression(
        C=1.0,
        solver="lbfgs",
        class_weight="balanced",
        max_iter=1000,
        random_state=seed
    )
    lr_clf.fit(X_train_scaled, y_train)

    lr_preds = lr_clf.predict(X_test_scaled)
    lr_probs = lr_clf.predict_proba(X_test_scaled)[:, 1]

    lr_coef_sum = np.sum(np.abs(lr_clf.coef_[0]))
    lr_importances = {
        col: round(float(abs(coef) / (lr_coef_sum if lr_coef_sum > 0 else 1.0)), 4)
        for col, coef in zip(FEATURE_COLUMNS, lr_clf.coef_[0])
    }

    lr_metrics = {
        "model_name": "Logistic Regression",
        "model_type": "Linear Baseline Classifier",
        "accuracy": round(float(accuracy_score(y_test, lr_preds)), 4),
        "precision": round(float(precision_score(y_test, lr_preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, lr_preds, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, lr_preds, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, lr_probs)), 4),
        "confusion_matrix": confusion_matrix(y_test, lr_preds).tolist(),
        "feature_importances": lr_importances
    }

    # Save models and preprocessor using joblib
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(iso_forest, ISOLATION_FOREST_PATH)
    joblib.dump(rf_clf, RANDOM_FOREST_PATH)
    joblib.dump(lr_clf, LOGISTIC_REGRESSION_PATH)

    # Build evaluation report
    report = {
        "models": [rf_metrics, lr_metrics, iso_metrics],
        "dataset_info": {
            "total_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "feature_count": len(FEATURE_COLUMNS),
            "feature_names": FEATURE_COLUMNS,
            "failure_rate": round(float(np.mean(y)), 4),
            "dataset_type": "Synthetic Infrastructure Telemetry (Reproducible, Fixed Seed 42)"
        },
        "last_trained": datetime.now().isoformat(),
        "isolation_forest_summary": {
            "n_estimators": 150,
            "contamination": 0.20,
            "anomaly_threshold": round(float(np.percentile(iso_scores, 80)), 4)
        }
    }

    with open(METRICS_REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    return report

if __name__ == "__main__":
    rep = train_and_evaluate_all()
    print("Training finished successfully:")
    for m in rep["models"]:
        print(f"-> {m['model_name']}: Acc={m['accuracy']}, Prec={m['precision']}, Rec={m['recall']}, F1={m['f1_score']}, AUC={m['roc_auc']}")
