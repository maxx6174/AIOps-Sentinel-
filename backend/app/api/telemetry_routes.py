from fastapi import APIRouter
from app.engine.telemetry_service import TelemetryService
from app.ml.inference import MLInferenceEngine
from app.models.schemas import TelemetrySnapshot

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])

@router.get("/snapshot", response_model=TelemetrySnapshot)
def get_telemetry_snapshot():
    """Returns the latest aggregated infrastructure telemetry, rolling history, and service health."""
    service = TelemetryService.get_instance()
    ml_engine = MLInferenceEngine.get_instance()
    return service.get_snapshot(ml_engine)

@router.get("/history")
def get_telemetry_history():
    """Returns recent time-series telemetry points for charting."""
    service = TelemetryService.get_instance()
    return {"history": service.get_history()}

@router.get("/current")
def get_current_telemetry():
    """Returns current active telemetry point."""
    service = TelemetryService.get_instance()
    return service.get_current_point()
