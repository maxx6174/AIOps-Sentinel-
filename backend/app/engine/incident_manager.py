import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class IncidentManager:
    _instance = None

    def __init__(self):
        self.incidents: List[Dict[str, Any]] = []
        self._seed_initial_incidents()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _seed_initial_incidents(self):
        """Seeds realistic historical incidents for immediate review and demonstration."""
        now = datetime.now()
        
        self.incidents = [
            {
                "id": "INC-849201",
                "timestamp": (now - timedelta(hours=2, minutes=14)).strftime("%Y-%m-%d %H:%M:%S"),
                "title": "CPU Saturation on API Gateway Cluster",
                "severity": "CRITICAL",
                "status": "RESOLVED",
                "affected_metric": "CPU Utilization",
                "observed_value": "96.4%",
                "root_cause": "Runaway regex parsing on ingress JWT header validation",
                "action_taken": "Patched regex pattern and scaled deployment to 8 pods"
            },
            {
                "id": "INC-791042",
                "timestamp": (now - timedelta(hours=5, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
                "title": "Progressive Heap Leak in Payment Engine",
                "severity": "HIGH",
                "status": "RESOLVED",
                "affected_metric": "Memory Utilization",
                "observed_value": "93.8%",
                "root_cause": "Unbounded retention in customer session hash map",
                "action_taken": "Introduced LRU eviction with 15-minute TTL"
            },
            {
                "id": "INC-652391",
                "timestamp": (now - timedelta(hours=14, minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
                "title": "Inter-Region Network Degradation",
                "severity": "WARNING",
                "status": "RESOLVED",
                "affected_metric": "Network Latency",
                "observed_value": "342 ms",
                "root_cause": "BGP route flap between US-East and EU-West VPC peering",
                "action_taken": "Rerouted traffic through dedicated transit gateway"
            }
        ]

    def create_incident_from_analysis(self, analysis: Dict[str, Any], telemetry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Automatically registers a new active incident if risk is HIGH or CRITICAL."""
        risk_level = analysis["risk_level"]
        if risk_level not in ("High", "Critical"):
            return None

        # Check if an active incident with same probable root cause was created in the last 2 minutes to prevent spam
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for inc in self.incidents:
            if inc["status"] == "ACTIVE" and inc["root_cause"] == analysis["probable_root_cause"]:
                # Already active incident exists
                return inc

        top_factor = analysis["contributing_factors"][0] if analysis["contributing_factors"] else None
        metric_name = top_factor["metric"].replace("_", " ").title() if top_factor else "System Health"
        observed_val = f"{top_factor['observed_value']}{top_factor['unit']}" if top_factor else "Abnormal"

        severity_map = {"Critical": "CRITICAL", "High": "HIGH", "Moderate": "WARNING", "Low": "INFO"}
        severity = severity_map.get(risk_level, "WARNING")

        new_incident = {
            "id": analysis["incident_id"],
            "timestamp": now_str,
            "title": f"{analysis['probable_root_cause']} Detected",
            "severity": severity,
            "status": "ACTIVE",
            "affected_metric": metric_name,
            "observed_value": observed_val,
            "root_cause": analysis["probable_root_cause"],
            "action_taken": None
        }

        self.incidents.insert(0, new_incident)
        # Keep incident log bounded
        if len(self.incidents) > 50:
            self.incidents = self.incidents[:50]

        return new_incident

    def get_all_incidents(self) -> List[Dict[str, Any]]:
        return self.incidents

    def update_incident_status(self, incident_id: str, new_status: str, action_taken: Optional[str] = None) -> Optional[Dict[str, Any]]:
        for inc in self.incidents:
            if inc["id"] == incident_id:
                inc["status"] = new_status
                if action_taken:
                    inc["action_taken"] = action_taken
                return inc
        return None
