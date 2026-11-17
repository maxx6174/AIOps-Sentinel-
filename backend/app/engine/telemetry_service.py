import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.config import MONITORED_SERVICES, METRIC_BASELINES

class TelemetryService:
    _instance = None

    def __init__(self):
        self.history_size = 40
        self.history: List[Dict[str, Any]] = []
        self._initialize_baseline_history()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_baseline_history(self):
        """Prepopulates smooth historical telemetry points for realistic time-series charts."""
        now = datetime.now()
        np.random.seed(42)

        for i in range(self.history_size):
            t = (now - timedelta(seconds=(self.history_size - i) * 3)).strftime("%H:%M:%S")
            cpu = float(np.clip(np.random.normal(42.0, 3.0), 20.0, 70.0))
            mem = float(np.clip(np.random.normal(54.0, 2.0), 30.0, 75.0))
            disk = float(np.clip(np.random.normal(59.0, 1.0), 40.0, 80.0))
            lat = float(np.clip(np.random.normal(44.0, 5.0), 15.0, 90.0))
            err = float(np.clip(np.random.exponential(0.4), 0.0, 2.5))

            self.history.append({
                "timestamp": t,
                "cpu_utilization": round(cpu, 1),
                "memory_utilization": round(mem, 1),
                "disk_utilization": round(disk, 1),
                "network_latency": round(lat, 1),
                "error_rate": round(err, 2),
                "service_id": "srv-gateway"
            })

    def get_current_point(self) -> Dict[str, Any]:
        if self.history:
            return self.history[-1]
        now_str = datetime.now().strftime("%H:%M:%S")
        return {
            "timestamp": now_str,
            "cpu_utilization": 42.0,
            "memory_utilization": 54.0,
            "disk_utilization": 59.0,
            "network_latency": 45.0,
            "error_rate": 0.5,
            "service_id": "srv-gateway"
        }

    def record_telemetry_point(self, point: Dict[str, Any]):
        """Pushes a new telemetry point and trims rolling window buffer."""
        self.history.append(point)
        if len(self.history) > self.history_size:
            self.history.pop(0)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def get_services_health(self, current_point: Dict[str, Any], risk_level: str) -> List[Dict[str, Any]]:
        """Calculates granular health for all monitored microservices based on system telemetry."""
        cpu = current_point["cpu_utilization"]
        mem = current_point["memory_utilization"]
        lat = current_point["network_latency"]
        err = current_point["error_rate"]

        services_status = []
        for s in MONITORED_SERVICES:
            sid = s["id"]
            # Derive service-specific metrics with realistic variations
            if sid == "srv-gateway":
                s_status = "critical" if (lat > 250 or err > 5.0) else ("warning" if lat > 120 else "healthy")
                s_lat = round(lat, 1)
                s_err = round(err, 2)
                uptime = 99.98
            elif sid == "srv-auth":
                s_status = "critical" if cpu > 90 else ("warning" if cpu > 75 else "healthy")
                s_lat = round(lat * 0.7 + 5, 1)
                s_err = round(max(0.1, err * 0.5), 2)
                uptime = 99.99
            elif sid == "srv-payment":
                s_status = "critical" if (mem > 90 or err > 4.0) else ("warning" if mem > 80 else "healthy")
                s_lat = round(lat * 0.85 + 10, 1)
                s_err = round(err * 0.8, 2)
                uptime = 99.95
            elif sid == "srv-database":
                s_status = "critical" if (cpu > 90 and lat > 200) else ("warning" if cpu > 80 else "healthy")
                s_lat = round(max(5.0, lat * 0.4), 1)
                s_err = round(max(0.0, err * 0.2), 2)
                uptime = 99.99
            else:  # srv-cache
                s_status = "critical" if mem > 92 else ("warning" if mem > 82 else "healthy")
                s_lat = round(max(2.0, lat * 0.15), 1)
                s_err = 0.05
                uptime = 100.0

            services_status.append({
                "id": s["id"],
                "name": s["name"],
                "type": s["type"],
                "endpoint": s["endpoint"],
                "status": s_status,
                "latency": s_lat,
                "error_rate": s_err,
                "uptime": uptime
            })

        return services_status

    def get_snapshot(self, ml_inference_engine) -> Dict[str, Any]:
        """Assembles a full infrastructure telemetry snapshot including risk metrics and services."""
        curr = self.get_current_point()
        ml_res = ml_inference_engine.predict_single(
            cpu_utilization=curr["cpu_utilization"],
            memory_utilization=curr["memory_utilization"],
            disk_utilization=curr["disk_utilization"],
            network_latency=curr["network_latency"],
            error_rate=curr["error_rate"]
        )

        risk_score = ml_res["risk_score"]
        risk_level = ml_res["risk_level"]

        overall_health = "HEALTHY"
        if risk_level == "Critical":
            overall_health = "CRITICAL"
        elif risk_level in ("High", "Moderate"):
            overall_health = "WARNING"

        services = self.get_services_health(curr, risk_level)
        healthy_cnt = sum(1 for s in services if s["status"] == "healthy")
        warn_cnt = sum(1 for s in services if s["status"] == "warning")
        crit_cnt = sum(1 for s in services if s["status"] == "critical")

        return {
            "current": curr,
            "history": self.history,
            "overall_health": overall_health,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "services": services,
            "total_services": len(services),
            "healthy_count": healthy_cnt,
            "warning_count": warn_cnt,
            "critical_count": crit_cnt
        }
