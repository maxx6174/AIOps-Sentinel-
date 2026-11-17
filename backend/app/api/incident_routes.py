from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.engine.incident_manager import IncidentManager

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

class IncidentStatusUpdate(BaseModel):
    status: str  # "ACKNOWLEDGED", "RESOLVED"
    action_taken: Optional[str] = None

@router.get("")
def list_incidents():
    """Returns list of active, acknowledged, and historical infrastructure incidents."""
    mgr = IncidentManager.get_instance()
    return {"incidents": mgr.get_all_incidents()}

@router.patch("/{incident_id}/status")
def update_incident_status(incident_id: str, body: IncidentStatusUpdate):
    """Updates resolution status of a specific infrastructure incident."""
    mgr = IncidentManager.get_instance()
    res = mgr.update_incident_status(incident_id, body.status, body.action_taken)
    if not res:
        raise HTTPException(status_code=404, detail="Incident not found")
    return res
