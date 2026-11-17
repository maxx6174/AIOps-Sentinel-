from fastapi import APIRouter
from app.engine.simulation_engine import SimulationEngine, SCENARIO_CONFIGS
from app.models.schemas import SimulationControlRequest

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

@router.get("/scenarios")
def get_available_scenarios():
    """Lists the 5 selectable failure and baseline scenarios."""
    return [
        {"id": k, **v} for k, v in SCENARIO_CONFIGS.items()
    ]

@router.get("/status")
def get_simulation_status():
    """Returns current active simulation state, telemetry point, and live ML inference."""
    engine = SimulationEngine.get_instance()
    return engine.get_status()

@router.post("/control")
def control_simulation(req: SimulationControlRequest):
    """Executes state transitions: start, pause, resume, reset across the 5 failure scenarios."""
    engine = SimulationEngine.get_instance()
    action = req.action.lower()

    if action == "start":
        return engine.start(req.scenario)
    elif action == "pause":
        return engine.pause()
    elif action == "resume":
        return engine.resume()
    elif action == "reset":
        return engine.reset()
    else:
        return engine.get_status()

@router.post("/step")
def step_simulation():
    """Advances simulation by one tick, recalculates ML inference, and records telemetry."""
    engine = SimulationEngine.get_instance()
    return engine.step()
