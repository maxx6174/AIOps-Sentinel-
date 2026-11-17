import json
from datetime import datetime
from fastapi import APIRouter
from app.config import METRICS_REPORT_PATH
from app.models.schemas import PredictionRequest, PredictionResponse, ModelComparisonResponse
from app.ml.inference import MLInferenceEngine
from app.ml.trainer import train_and_evaluate_all
from app.engine.root_cause_engine import generate_root_cause_analysis

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

@router.post("/predict", response_model=PredictionResponse)
def predict_telemetry(req: PredictionRequest):
    """
    Executes real machine learning inference for arbitrary telemetry inputs:
    - Isolation Forest (Anomaly detection)
    - Random Forest (Failure probability & risk level)
    - Logistic Regression (Baseline comparison)
    - Explainable AI & Root Cause Analysis
    """
    ml_engine = MLInferenceEngine.get_instance()
    ml_res = ml_engine.predict_single(
        cpu_utilization=req.cpu_utilization,
        memory_utilization=req.memory_utilization,
        disk_utilization=req.disk_utilization,
        network_latency=req.network_latency,
        error_rate=req.error_rate
    )

    analysis = generate_root_cause_analysis(
        cpu=req.cpu_utilization,
        memory=req.memory_utilization,
        disk=req.disk_utilization,
        latency=req.network_latency,
        error_rate=req.error_rate,
        ml_result=ml_res,
        service_id=req.service_id or "manual-check"
    )

    return {
        "prediction_id": analysis["incident_id"],
        "timestamp": datetime.now().isoformat(),
        "failure_predicted": ml_res["failure_predicted"],
        "failure_probability": ml_res["failure_probability"],
        "risk_level": ml_res["risk_level"],
        "anomaly_detected": ml_res["anomaly_detected"],
        "anomaly_score": ml_res["anomaly_score"],
        "logistic_baseline_probability": ml_res["logistic_baseline_probability"],
        "model_agreement": ml_res["model_agreement"],
        "explanation": analysis
    }

@router.get("/metrics", response_model=ModelComparisonResponse)
def get_model_evaluation_metrics():
    """
    Returns verified model evaluation results:
    - Accuracy, Precision, Recall, F1-Score, ROC-AUC
    - Confusion Matrix for Random Forest, Logistic Regression, and Isolation Forest
    - Feature importances
    - Training metadata
    """
    if not METRICS_REPORT_PATH.exists():
        train_and_evaluate_all()

    with open(METRICS_REPORT_PATH, "r") as f:
        metrics = json.load(f)

    return metrics

@router.post("/retrain")
def retrain_models():
    """Triggers complete model retraining, re-evaluation, and artifact persistence."""
    report = train_and_evaluate_all()
    # Refresh in-memory inference engine
    MLInferenceEngine.get_instance().load_models()
    return {"message": "All machine learning models successfully retrained and verified.", "report": report}
