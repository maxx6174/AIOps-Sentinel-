from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.telemetry_routes import router as telemetry_router
from app.api.ml_routes import router as ml_router
from app.api.simulation_routes import router as simulation_router
from app.api.incident_routes import router as incident_router
from app.api.data_routes import router as data_router
from app.ml.inference import MLInferenceEngine

app = FastAPI(
    title="AIOps Sentinel API",
    description="Explainable AI-Powered Infrastructure Failure Prediction and Intelligent Root Cause Analysis Platform",
    version="1.0.0"
)

# CORS configuration - Allows requests from Vite dev server and production deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all modular routers
app.include_router(telemetry_router)
app.include_router(ml_router)
app.include_router(simulation_router)
app.include_router(incident_router)
app.include_router(data_router)

# Eagerly initialize ML engine
try:
    MLInferenceEngine.get_instance()
except Exception as e:
    print(f"Warning initializing ML engine: {e}")

@app.get("/")
def root():
    return {
        "project": "AIOps Sentinel",
        "title": "Explainable AI-Powered Infrastructure Failure Prediction and Intelligent Root Cause Analysis Platform",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for production load balancers and deployment verification."""
    return {
        "status": "HEALTHY",
        "service": "aiops-sentinel-backend",
        "ml_engine_loaded": MLInferenceEngine.get_instance().rf_clf is not None
    }
