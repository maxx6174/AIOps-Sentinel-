import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Dataset paths
SYNTHETIC_DATASET_PATH = DATA_DIR / "synthetic_infrastructure_telemetry.csv"
SAMPLE_CSV_PATH = DATA_DIR / "sample_infrastructure_metrics.csv"

# Model paths
ISOLATION_FOREST_PATH = SAVED_MODELS_DIR / "isolation_forest.joblib"
RANDOM_FOREST_PATH = SAVED_MODELS_DIR / "random_forest.joblib"
LOGISTIC_REGRESSION_PATH = SAVED_MODELS_DIR / "logistic_regression.joblib"
SCALER_PATH = SAVED_MODELS_DIR / "scaler.joblib"
METRICS_REPORT_PATH = SAVED_MODELS_DIR / "evaluation_metrics.json"

# Features definition
FEATURE_COLUMNS = [
    "cpu_utilization",
    "memory_utilization",
    "disk_utilization",
    "network_latency",
    "error_rate"
]

# Normal infrastructure metric baselines and operational thresholds
METRIC_BASELINES = {
    "cpu_utilization": {"normal_mean": 42.0, "normal_std": 10.0, "warning": 75.0, "critical": 90.0, "unit": "%"},
    "memory_utilization": {"normal_mean": 55.0, "normal_std": 8.0, "warning": 80.0, "critical": 92.0, "unit": "%"},
    "disk_utilization": {"normal_mean": 60.0, "normal_std": 5.0, "warning": 85.0, "critical": 95.0, "unit": "%"},
    "network_latency": {"normal_mean": 45.0, "normal_std": 12.0, "warning": 150.0, "critical": 300.0, "unit": "ms"},
    "error_rate": {"normal_mean": 0.8, "normal_std": 0.4, "warning": 3.0, "critical": 8.0, "unit": "%"}
}

# Monitored microservices
MONITORED_SERVICES = [
    {"id": "srv-gateway", "name": "API Gateway", "type": "Edge Ingress", "endpoint": "/api/v1"},
    {"id": "srv-auth", "name": "Authentication Service", "type": "Identity Provider", "endpoint": "/auth"},
    {"id": "srv-payment", "name": "Payment Engine", "type": "Core Business", "endpoint": "/payments"},
    {"id": "srv-database", "name": "PostgreSQL Primary", "type": "Relational DB", "endpoint": "tcp://db:5432"},
    {"id": "srv-cache", "name": "Redis Distributed Cache", "type": "In-Memory Store", "endpoint": "tcp://cache:6379"}
]
