# AIOps Sentinel &mdash; RESTful API Documentation

The backend service is powered by **FastAPI** with automatic interactive OpenAPI documentation available at `/docs` and ReDoc at `/redoc`.

Base URL (Local): `http://127.0.0.1:8000`

---

## 1. System Endpoints

### `GET /health`
Returns system operational state and verification that ML weights are loaded.
- **Response `200 OK`**:
```json
{
  "status": "HEALTHY",
  "service": "aiops-sentinel-backend",
  "ml_engine_loaded": true
}
```

---

## 2. Infrastructure Telemetry Endpoints

### `GET /api/telemetry/snapshot`
Aggregates the current infrastructure state, rolling history buffer, composite risk score, and health status for all 5 monitored services.
- **Response `200 OK`**:
```json
{
  "current": {
    "timestamp": "14:22:10",
    "cpu_utilization": 43.2,
    "memory_utilization": 54.1,
    "disk_utilization": 59.3,
    "network_latency": 44.8,
    "error_rate": 0.42,
    "service_id": "srv-gateway"
  },
  "history": [ ... ],
  "overall_health": "HEALTHY",
  "risk_score": 12.4,
  "risk_level": "Low",
  "services": [
    {
      "id": "srv-gateway",
      "name": "API Gateway",
      "type": "Edge Ingress",
      "endpoint": "/api/v1",
      "status": "healthy",
      "latency": 44.8,
      "error_rate": 0.42,
      "uptime": 99.98
    }
  ],
  "total_services": 5,
  "healthy_count": 5,
  "warning_count": 0,
  "critical_count": 0
}
```

---

## 3. Machine Learning & Explainable AI Endpoints

### `POST /api/ml/predict`
Executes real-time inference across Random Forest, Logistic Regression, and Isolation Forest, returning calibrated failure probability and full Explainable AI (XAI) root cause analysis.
- **Request Body**:
```json
{
  "cpu_utilization": 94.0,
  "memory_utilization": 87.0,
  "disk_utilization": 60.0,
  "network_latency": 320.0,
  "error_rate": 6.5
}
```
- **Response `200 OK`**:
```json
{
  "prediction_id": "INC-7C91A0",
  "timestamp": "2026-11-17T22:45:00",
  "failure_predicted": true,
  "failure_probability": 0.985,
  "risk_level": "Critical",
  "anomaly_detected": true,
  "anomaly_score": 92.4,
  "logistic_baseline_probability": 0.971,
  "model_agreement": true,
  "explanation": {
    "incident_id": "INC-7C91A0",
    "probable_root_cause": "Cascading Resource Exhaustion & System Saturation",
    "supporting_evidence": [
      "Cpu Utilization is observed at 94.0% (113.6% elevated from baseline 42.0%, exceeding critical threshold).",
      "Network Latency is observed at 320.0ms (611.1% elevated from baseline 45.0ms, exceeding critical threshold)."
    ],
    "hypotheses": [
      "Severe concurrent compute and memory contention causing kernel thread context thrashing.",
      "Upstream traffic surge exceeding gateway throughput capacity."
    ],
    "recommended_actions": [
      "Trigger automated horizontal pod autoscaling (HPA) to shed load across redundant replicas.",
      "Enable rate-limiting and circuit breakers at the API Gateway."
    ],
    "four_questions": {
      "what_is_happening": "Infrastructure health is critical. CPU (94%) and Memory (87%) are heavily saturated...",
      "why_is_it_occurring": "Multi-tiered resource saturation where compute execution units have exhausted headroom...",
      "what_could_happen_next": "Immediate service blackout or node crash predicted with 98% probability...",
      "what_action_should_be_taken": "Trigger automated horizontal pod autoscaling (HPA)..."
    }
  }
}
```

### `GET /api/ml/metrics`
Returns benchmark evaluation metrics for all trained models (accuracy, precision, recall, F1, ROC-AUC, confusion matrices, and feature importances).

### `POST /api/ml/retrain`
Triggers synchronous retraining and evaluation of all models, updating serialized weights and metrics.

---

## 4. Live Simulation Endpoints

### `GET /api/simulation/scenarios`
Returns the 5 available failure and baseline demonstration scenarios:
1. `normal`: Normal Operation
2. `cpu_overload`: CPU Overload & Thread Starvation
3. `memory_leak`: Memory Leak & GC Thrashing
4. `network_failure`: Network Latency & Packet Loss
5. `combined_failure`: Combined Infrastructure Failure

### `POST /api/simulation/control`
- **Request Body**: `{"action": "start" | "pause" | "resume" | "reset", "scenario": "cpu_overload"}`

### `POST /api/simulation/step`
Advances simulation state by one tick, generates active telemetry point, executes ML pipeline, and updates system telemetry.

---

## 5. Data & Reporting Endpoints

### `GET /api/data/sample-csv`
Downloads a sample CSV containing 120 rows of realistic infrastructure metrics ready for upload.

### `POST /api/data/upload`
Accepts a multipart CSV file with required headers (`cpu_utilization`, `memory_utilization`, `disk_utilization`, `network_latency`, `error_rate`), runs batch anomaly detection and failure classification, and returns aggregated statistics.

### `GET /api/data/export-report`
Downloads a timestamped diagnostic summary audit report in text format.
