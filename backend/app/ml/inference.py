import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List

from app.config import (
    FEATURE_COLUMNS,
    METRIC_BASELINES,
    ISOLATION_FOREST_PATH,
    RANDOM_FOREST_PATH,
    LOGISTIC_REGRESSION_PATH,
    SCALER_PATH
)
from app.ml.trainer import train_and_evaluate_all

class MLInferenceEngine:
    _instance = None

    def __init__(self):
        self.scaler = None
        self.iso_forest = None
        self.rf_clf = None
        self.lr_clf = None
        self.load_models()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_models(self):
        """Loads serialized models, training them first if missing."""
        if not (ISOLATION_FOREST_PATH.exists() and RANDOM_FOREST_PATH.exists() and SCALER_PATH.exists()):
            train_and_evaluate_all()

        self.scaler = joblib.load(SCALER_PATH)
        self.iso_forest = joblib.load(ISOLATION_FOREST_PATH)
        self.rf_clf = joblib.load(RANDOM_FOREST_PATH)
        self.lr_clf = joblib.load(LOGISTIC_REGRESSION_PATH)

    def predict_single(
        self,
        cpu_utilization: float,
        memory_utilization: float,
        disk_utilization: float,
        network_latency: float,
        error_rate: float
    ) -> Dict[str, Any]:
        """
        Executes unified ML inference across all trained models:
        1. Feature scaling
        2. Isolation Forest anomaly scoring
        3. Random Forest failure probability & binary classification
        4. Logistic Regression baseline prediction
        5. Relative feature contribution computation
        """
        raw_features = np.array([[
            cpu_utilization,
            memory_utilization,
            disk_utilization,
            network_latency,
            error_rate
        ]])

        scaled_features = self.scaler.transform(raw_features)

        # 1. Isolation Forest inference
        iso_pred_raw = self.iso_forest.predict(scaled_features)[0]  # -1 (anomaly) or 1 (normal)
        anomaly_detected = bool(iso_pred_raw == -1)
        raw_iso_score = -float(self.iso_forest.score_samples(scaled_features)[0])
        # Normalized anomaly score (0 - 100)
        anomaly_score = round(float(np.clip((raw_iso_score - 0.35) / 0.40 * 100.0, 0.0, 100.0)), 2)

        # 2. Random Forest inference (Primary)
        rf_prob = float(self.rf_clf.predict_proba(scaled_features)[0][1])
        failure_predicted = bool(rf_prob >= 0.50)

        # 3. Logistic Regression inference (Baseline comparison)
        lr_prob = float(self.lr_clf.predict_proba(scaled_features)[0][1])

        # 4. Determine Composite Risk Level
        risk_score = round((rf_prob * 0.7 + (anomaly_score / 100.0) * 0.3) * 100.0, 1)
        if risk_score >= 75.0 or rf_prob >= 0.75:
            risk_level = "Critical"
        elif risk_score >= 50.0 or rf_prob >= 0.50:
            risk_level = "High"
        elif risk_score >= 25.0 or anomaly_detected:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # 5. Local feature attribution
        feature_contributions = self._compute_feature_contributions(
            cpu_utilization,
            memory_utilization,
            disk_utilization,
            network_latency,
            error_rate,
            scaled_features[0]
        )

        return {
            "failure_predicted": failure_predicted,
            "failure_probability": round(rf_prob, 4),
            "risk_level": risk_level,
            "risk_score": risk_score,
            "anomaly_detected": anomaly_detected,
            "anomaly_score": anomaly_score,
            "logistic_baseline_probability": round(lr_prob, 4),
            "model_agreement": (failure_predicted == (lr_prob >= 0.50)),
            "contributions": feature_contributions
        }

    def _compute_feature_contributions(
        self,
        cpu: float,
        memory: float,
        disk: float,
        latency: float,
        error_rate: float,
        scaled_vec: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Computes local feature contribution combining global RF feature importances
        and z-score deviation from operational baseline.
        """
        raw_vals = [cpu, memory, disk, latency, error_rate]
        contributions = []

        rf_importances = self.rf_clf.feature_importances_

        for i, col in enumerate(FEATURE_COLUMNS):
            val = raw_vals[i]
            base_info = METRIC_BASELINES[col]
            base_mean = base_info["normal_mean"]
            base_std = base_info["normal_std"]
            warn_val = base_info["warning"]
            crit_val = base_info["critical"]

            # Deviation relative to standard deviation
            z_dev = abs(val - base_mean) / base_std
            pct_dev = round(((val - base_mean) / base_mean) * 100.0, 1)

            # Local attribution weight: importances weighted by scaled deviation
            local_impact = float(rf_importances[i] * max(0.0, scaled_vec[i]))

            is_anom = val >= warn_val
            status = "CRITICAL" if val >= crit_val else ("WARNING" if val >= warn_val else "NORMAL")

            contributions.append({
                "metric": col,
                "observed_value": round(val, 2),
                "baseline_value": base_mean,
                "deviation_percent": pct_dev,
                "importance_score": round(float(rf_importances[i]), 4),
                "local_impact": round(local_impact, 4),
                "is_anomaly": is_anom,
                "status": status,
                "unit": base_info["unit"]
            })

        # Sort contributions by local impact descending
        contributions.sort(key=lambda x: (x["status"] == "CRITICAL", x["local_impact"]), reverse=True)
        return contributions

    def predict_batch_df(self, df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Executes batch ML inference on uploaded CSV DataFrame."""
        results = []
        risk_counts = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
        total_anomalies = 0
        total_failures = 0

        X = df[FEATURE_COLUMNS].values
        X_scaled = self.scaler.transform(X)

        iso_preds_raw = self.iso_forest.predict(X_scaled)
        iso_scores = -self.iso_forest.score_samples(X_scaled)
        rf_probs = self.rf_clf.predict_proba(X_scaled)[:, 1]

        for idx in range(len(df)):
            row = df.iloc[idx]
            rf_prob = float(rf_probs[idx])
            iso_anom = bool(iso_preds_raw[idx] == -1)
            raw_score = float(iso_scores[idx])
            anom_score = round(float(np.clip((raw_score - 0.35) / 0.40 * 100.0, 0.0, 100.0)), 1)
            fail_pred = bool(rf_prob >= 0.50)

            risk_val = round((rf_prob * 0.7 + (anom_score / 100.0) * 0.3) * 100.0, 1)
            if risk_val >= 75.0 or rf_prob >= 0.75:
                r_level = "Critical"
            elif risk_val >= 50.0 or rf_prob >= 0.50:
                r_level = "High"
            elif risk_val >= 25.0 or iso_anom:
                r_level = "Moderate"
            else:
                r_level = "Low"

            risk_counts[r_level] += 1
            if iso_anom:
                total_anomalies += 1
            if fail_pred:
                total_failures += 1

            # Identify primary contributing metric
            cpu_val = float(row["cpu_utilization"])
            mem_val = float(row["memory_utilization"])
            net_val = float(row["network_latency"])
            err_val = float(row["error_rate"])
            disk_val = float(row["disk_utilization"])

            deviations = [
                ("CPU", cpu_val / METRIC_BASELINES["cpu_utilization"]["warning"]),
                ("Memory", mem_val / METRIC_BASELINES["memory_utilization"]["warning"]),
                ("Latency", net_val / METRIC_BASELINES["network_latency"]["warning"]),
                ("Error Rate", err_val / max(0.1, METRIC_BASELINES["error_rate"]["warning"])),
                ("Disk", disk_val / METRIC_BASELINES["disk_utilization"]["warning"])
            ]
            primary_factor = max(deviations, key=lambda x: x[1])[0]

            results.append({
                "row_index": idx + 1,
                "timestamp": str(row.get("timestamp", f"T+{idx * 2}m")),
                "cpu_utilization": round(cpu_val, 2),
                "memory_utilization": round(mem_val, 2),
                "disk_utilization": round(disk_val, 2),
                "network_latency": round(net_val, 2),
                "error_rate": round(err_val, 2),
                "anomaly_detected": iso_anom,
                "anomaly_score": anom_score,
                "failure_predicted": fail_pred,
                "failure_probability": round(rf_prob, 4),
                "risk_level": r_level,
                "primary_factor": primary_factor
            })

        summary = {
            "total_records": len(df),
            "anomalies_detected": total_anomalies,
            "failures_predicted": total_failures,
            "risk_breakdown": risk_counts,
            "average_metrics": {
                "cpu_utilization": round(float(df["cpu_utilization"].mean()), 2),
                "memory_utilization": round(float(df["memory_utilization"].mean()), 2),
                "disk_utilization": round(float(df["disk_utilization"].mean()), 2),
                "network_latency": round(float(df["network_latency"].mean()), 2),
                "error_rate": round(float(df["error_rate"].mean()), 2)
            }
        }

        return results, summary
