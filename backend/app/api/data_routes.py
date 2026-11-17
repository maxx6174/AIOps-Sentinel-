import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.config import SAMPLE_CSV_PATH, FEATURE_COLUMNS
from app.ml.inference import MLInferenceEngine
from app.models.schemas import CSVAnalysisResponse

router = APIRouter(prefix="/api/data", tags=["Data & Reports"])

@router.get("/sample-csv")
def download_sample_csv():
    """Provides downloadable sample infrastructure telemetry CSV for user testing."""
    if not SAMPLE_CSV_PATH.exists():
        from app.ml.dataset_generator import save_default_datasets
        save_default_datasets()

    return FileResponse(
        path=str(SAMPLE_CSV_PATH),
        filename="aiops_sample_telemetry.csv",
        media_type="text/csv"
    )

@router.post("/upload", response_model=CSVAnalysisResponse)
async def upload_and_analyze_csv(file: UploadFile = File(...)):
    """
    Validates uploaded infrastructure telemetry CSV, checks schema,
    executes batch Anomaly Detection & Failure Prediction, and returns structured findings.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are accepted.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    # Schema validation
    missing_cols = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=422,
            detail=f"Uploaded CSV is missing required telemetry columns: {', '.join(missing_cols)}. "
                   f"Expected columns: {', '.join(FEATURE_COLUMNS)}"
        )

    # Clean and validate numerical bounds
    for col in FEATURE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    if df[FEATURE_COLUMNS].isnull().any().any():
        df = df.dropna(subset=FEATURE_COLUMNS)

    if len(df) == 0:
        raise HTTPException(status_code=400, detail="Uploaded CSV contains zero valid numeric rows.")

    ml_engine = MLInferenceEngine.get_instance()
    row_results, summary = ml_engine.predict_batch_df(df)

    return {
        "filename": file.filename,
        "total_records": summary["total_records"],
        "anomalies_detected": summary["anomalies_detected"],
        "failures_predicted": summary["failures_predicted"],
        "risk_breakdown": summary["risk_breakdown"],
        "average_metrics": summary["average_metrics"],
        "sample_results": row_results[:100]  # First 100 records for display
    }

@router.get("/export-report")
def export_analysis_report():
    """Generates an executive ASCII / CSV summary report for download."""
    ml_engine = MLInferenceEngine.get_instance()
    t_svc = MLInferenceEngine.get_instance()
    from app.engine.telemetry_service import TelemetryService
    snap = TelemetryService.get_instance().get_snapshot(ml_engine)

    buffer = io.StringIO()
    buffer.write("=========================================================================\n")
    buffer.write("          AIOPS SENTINEL - INFRASTRUCTURE AUDIT & RISK REPORT            \n")
    buffer.write("=========================================================================\n\n")
    buffer.write(f"Generated At: {snap['current']['timestamp']}\n")
    buffer.write(f"Infrastructure Health Status: {snap['overall_health']}\n")
    buffer.write(f"System Risk Score: {snap['risk_score']} / 100\n\n")

    buffer.write("--- CURRENT TELEMETRY SNAPSHOT ---\n")
    curr = snap['current']
    buffer.write(f"CPU Utilization:    {curr['cpu_utilization']}%\n")
    buffer.write(f"Memory Utilization: {curr['memory_utilization']}%\n")
    buffer.write(f"Disk Utilization:   {curr['disk_utilization']}%\n")
    buffer.write(f"Network Latency:    {curr['network_latency']} ms\n")
    buffer.write(f"Error Rate:         {curr['error_rate']}%\n\n")

    buffer.write("--- MONITORED MICROSERVICES ---\n")
    for s in snap['services']:
        buffer.write(f"[{s['status'].upper():8s}] {s['name']:28s} | Latency: {s['latency']:5.1f}ms | Error: {s['error_rate']:4.2f}% | Uptime: {s['uptime']}%\n")
    buffer.write("\n=========================================================================\n")

    buffer.seek(0)
    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode("utf-8")),
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=aiops_infrastructure_report.txt"}
    )
