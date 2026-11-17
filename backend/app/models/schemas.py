from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TelemetryPoint(BaseModel):
    timestamp: str
    cpu_utilization: float = Field(..., ge=0.0, le=100.0, description="CPU usage in %")
    memory_utilization: float = Field(..., ge=0.0, le=100.0, description="Memory usage in %")
    disk_utilization: float = Field(..., ge=0.0, le=100.0, description="Disk usage in %")
    network_latency: float = Field(..., ge=0.0, description="Network round-trip latency in ms")
    error_rate: float = Field(..., ge=0.0, le=100.0, description="Application HTTP error rate in %")
    service_id: Optional[str] = "srv-gateway"

class ServiceHealth(BaseModel):
    id: str
    name: str
    type: str
    endpoint: str
    status: str  # "healthy", "warning", "critical"
    latency: float
    error_rate: float
    uptime: float

class TelemetrySnapshot(BaseModel):
    current: TelemetryPoint
    history: List[TelemetryPoint]
    overall_health: str  # "HEALTHY", "WARNING", "CRITICAL"
    risk_score: float    # 0 to 100
    services: List[ServiceHealth]
    total_services: int
    healthy_count: int
    warning_count: int
    critical_count: int

class ContributingFactor(BaseModel):
    metric: str
    observed_value: float
    baseline_value: float
    deviation_percent: float
    importance_score: float
    is_anomaly: bool
    status: str

class FourQuestionsAnswer(BaseModel):
    what_is_happening: str
    why_is_it_occurring: str
    what_could_happen_next: str
    what_action_should_be_taken: str

class RootCauseAnalysis(BaseModel):
    incident_id: str
    timestamp: str
    risk_level: str  # "Low", "Moderate", "High", "Critical"
    failure_probability: float  # 0.0 to 1.0
    failure_predicted: bool
    anomaly_detected: bool
    anomaly_score: float
    contributing_factors: List[ContributingFactor]
    supporting_evidence: List[str]
    hypotheses: List[str]
    probable_root_cause: str
    recommended_actions: List[str]
    four_questions: FourQuestionsAnswer

class PredictionRequest(BaseModel):
    cpu_utilization: float = Field(..., ge=0.0, le=100.0)
    memory_utilization: float = Field(..., ge=0.0, le=100.0)
    disk_utilization: float = Field(..., ge=0.0, le=100.0)
    network_latency: float = Field(..., ge=0.0)
    error_rate: float = Field(..., ge=0.0, le=100.0)
    service_id: Optional[str] = "manual-check"

class PredictionResponse(BaseModel):
    prediction_id: str
    timestamp: str
    failure_predicted: bool
    failure_probability: float
    risk_level: str
    anomaly_detected: bool
    anomaly_score: float
    logistic_baseline_probability: float
    model_agreement: bool
    explanation: RootCauseAnalysis

class SimulationControlRequest(BaseModel):
    action: str  # "start", "pause", "resume", "reset"
    scenario: Optional[str] = "normal"  # "normal", "cpu_overload", "memory_leak", "network_failure", "combined_failure"

class SimulationStatus(BaseModel):
    scenario: str
    scenario_display_name: str
    state: str  # "running", "paused", "stopped"
    step: int
    max_steps: int
    progress_percent: float
    telemetry: TelemetryPoint
    analysis: RootCauseAnalysis

class IncidentItem(BaseModel):
    id: str
    timestamp: str
    title: str
    severity: str  # "INFO", "WARNING", "HIGH", "CRITICAL"
    status: str    # "ACTIVE", "ACKNOWLEDGED", "RESOLVED"
    affected_metric: str
    observed_value: str
    root_cause: str
    action_taken: Optional[str] = None

class ModelMetrics(BaseModel):
    model_name: str
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None
    confusion_matrix: List[List[int]]
    feature_importances: Optional[Dict[str, float]] = None

class ModelComparisonResponse(BaseModel):
    models: List[ModelMetrics]
    dataset_info: Dict[str, Any]
    last_trained: str
    isolation_forest_summary: Dict[str, Any]

class CSVRowResult(BaseModel):
    row_index: int
    timestamp: str
    cpu_utilization: float
    memory_utilization: float
    disk_utilization: float
    network_latency: float
    error_rate: float
    anomaly_detected: bool
    anomaly_score: float
    failure_predicted: bool
    failure_probability: float
    risk_level: str
    primary_factor: str

class CSVAnalysisResponse(BaseModel):
    filename: str
    total_records: int
    anomalies_detected: int
    failures_predicted: int
    risk_breakdown: Dict[str, int]
    average_metrics: Dict[str, float]
    sample_results: List[CSVRowResult]
