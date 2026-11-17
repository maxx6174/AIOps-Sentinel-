import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional

from app.engine.root_cause_engine import generate_root_cause_analysis
from app.engine.incident_manager import IncidentManager
from app.engine.telemetry_service import TelemetryService
from app.ml.inference import MLInferenceEngine

SCENARIO_CONFIGS = {
    "normal": {
        "display_name": "Normal Operation",
        "description": "Baseline nominal cluster workloads with standard Gaussian variation.",
        "max_steps": 30
    },
    "cpu_overload": {
        "display_name": "CPU Overload & Thread Starvation",
        "description": "Simulates compute runaway: algorithmic bottleneck driving CPU to 96% with request queueing.",
        "max_steps": 30
    },
    "memory_leak": {
        "display_name": "Memory Leak & GC Thrashing",
        "description": "Progressive heap consumption leading toward container Out-Of-Memory (OOM) termination.",
        "max_steps": 30
    },
    "network_failure": {
        "display_name": "Network Latency & Packet Loss",
        "description": "Upstream route flap causing round-trip latency surge to 700+ ms and elevated error rate.",
        "max_steps": 30
    },
    "combined_failure": {
        "display_name": "Combined Infrastructure Failure",
        "description": "Multi-tier cascade: concurrent compute saturation, memory exhaustion, and transport breakdown.",
        "max_steps": 30
    }
}

class SimulationEngine:
    _instance = None

    def __init__(self):
        self.scenario = "normal"
        self.state = "stopped"  # "stopped", "running", "paused"
        self.current_step = 0
        self.max_steps = 30
        self.latest_telemetry: Optional[Dict[str, Any]] = None
        self.latest_analysis: Optional[Dict[str, Any]] = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_scenario(self, scenario_name: str):
        if scenario_name in SCENARIO_CONFIGS:
            self.scenario = scenario_name
            self.max_steps = SCENARIO_CONFIGS[scenario_name]["max_steps"]
            self.current_step = 0

    def start(self, scenario_name: Optional[str] = None):
        if scenario_name and scenario_name in SCENARIO_CONFIGS:
            self.set_scenario(scenario_name)
        self.state = "running"
        return self.step()

    def pause(self):
        self.state = "paused"
        return self.get_status()

    def resume(self):
        self.state = "running"
        return self.step()

    def reset(self):
        self.current_step = 0
        self.state = "stopped"
        # Reset telemetry service baseline
        t_service = TelemetryService.get_instance()
        t_service._initialize_baseline_history()
        return self.step()

    def step(self) -> Dict[str, Any]:
        """
        Advances the simulation by one tick, generates realistic telemetry values
        based on active scenario progression, and executes the genuine ML pipeline.
        """
        t = self.current_step
        max_t = self.max_steps
        norm_prog = min(1.0, t / max_t)

        now_str = datetime.now().strftime("%H:%M:%S")

        # Compute trajectory based on active scenario
        if self.scenario == "normal":
            cpu = float(np.clip(42.0 + np.random.normal(0, 3.0), 25.0, 58.0))
            mem = float(np.clip(54.0 + np.random.normal(0, 2.0), 40.0, 65.0))
            disk = float(np.clip(59.0 + np.random.normal(0, 1.0), 45.0, 68.0))
            lat = float(np.clip(44.0 + np.random.normal(0, 4.0), 20.0, 75.0))
            err = float(np.clip(0.4 + np.random.exponential(0.3), 0.0, 1.8))

        elif self.scenario == "cpu_overload":
            # Progressive ramp up from 42% to ~97%
            cpu_target = 42.0 + (96.0 - 42.0) * (norm_prog ** 1.3)
            cpu = float(np.clip(cpu_target + np.random.normal(0, 2.0), 30.0, 99.5))
            mem = float(np.clip(54.0 + (norm_prog * 10.0) + np.random.normal(0, 2.0), 40.0, 72.0))
            disk = float(np.clip(59.0 + np.random.normal(0, 1.0), 45.0, 68.0))
            lat_target = 44.0 + (280.0 - 44.0) * (norm_prog ** 1.5)
            lat = float(np.clip(lat_target + np.random.normal(0, 8.0), 30.0, 380.0))
            err_target = 0.4 + (5.5 - 0.4) * (norm_prog ** 2.0)
            err = float(np.clip(err_target + np.random.normal(0, 0.4), 0.0, 8.0))

        elif self.scenario == "memory_leak":
            # Progressive linear leak from 54% to 98%
            mem_target = 54.0 + (98.0 - 54.0) * norm_prog
            mem = float(np.clip(mem_target + np.random.normal(0, 1.2), 45.0, 99.5))
            # CPU spikes intermittently as GC tries to free unreachable heap
            gc_spike = 25.0 * (norm_prog ** 2.0) * (1.0 if t % 3 == 0 else 0.3)
            cpu = float(np.clip(44.0 + gc_spike + np.random.normal(0, 2.5), 35.0, 88.0))
            disk = float(np.clip(59.0 + (norm_prog * 6.0) + np.random.normal(0, 1.0), 50.0, 75.0))
            lat_target = 44.0 + (180.0 - 44.0) * (norm_prog ** 1.8)
            lat = float(np.clip(lat_target + np.random.normal(0, 6.0), 30.0, 250.0))
            err_target = 0.4 + (7.0 - 0.4) * (norm_prog ** 2.2)
            err = float(np.clip(err_target + np.random.normal(0, 0.5), 0.0, 12.0))

        elif self.scenario == "network_failure":
            # Latency spikes rapidly to 750+ ms
            lat_target = 44.0 + (720.0 - 44.0) * (norm_prog ** 1.4)
            lat = float(np.clip(lat_target + np.random.normal(0, 15.0), 35.0, 950.0))
            err_target = 0.4 + (14.0 - 0.4) * (norm_prog ** 1.6)
            err = float(np.clip(err_target + np.random.normal(0, 0.8), 0.0, 22.0))
            cpu = float(np.clip(46.0 + np.random.normal(0, 3.0), 30.0, 65.0))
            mem = float(np.clip(55.0 + np.random.normal(0, 2.0), 40.0, 70.0))
            disk = float(np.clip(59.0 + np.random.normal(0, 1.0), 45.0, 68.0))

        else:  # combined_failure
            # Multi-resource saturation
            cpu = float(np.clip(42.0 + (97.0 - 42.0) * (norm_prog ** 1.2) + np.random.normal(0, 1.8), 35.0, 99.8))
            mem = float(np.clip(54.0 + (96.0 - 54.0) * (norm_prog ** 1.2) + np.random.normal(0, 1.5), 40.0, 99.5))
            disk = float(np.clip(59.0 + (92.0 - 59.0) * norm_prog + np.random.normal(0, 1.0), 50.0, 98.0))
            lat = float(np.clip(44.0 + (680.0 - 44.0) * (norm_prog ** 1.3) + np.random.normal(0, 14.0), 35.0, 850.0))
            err = float(np.clip(0.4 + (18.0 - 0.4) * (norm_prog ** 1.5) + np.random.normal(0, 0.9), 0.0, 30.0))

        telemetry_point = {
            "timestamp": now_str,
            "cpu_utilization": round(cpu, 1),
            "memory_utilization": round(mem, 1),
            "disk_utilization": round(disk, 1),
            "network_latency": round(lat, 1),
            "error_rate": round(err, 2),
            "service_id": "srv-gateway"
        }

        # Record in TelemetryService
        telemetry_svc = TelemetryService.get_instance()
        telemetry_svc.record_telemetry_point(telemetry_point)

        # Run REAL ML inference
        ml_engine = MLInferenceEngine.get_instance()
        ml_result = ml_engine.predict_single(
            cpu_utilization=cpu,
            memory_utilization=mem,
            disk_utilization=disk,
            network_latency=lat,
            error_rate=err
        )

        # Generate Explainable AI & Root Cause Analysis
        analysis = generate_root_cause_analysis(
            cpu=cpu,
            memory=mem,
            disk=disk,
            latency=lat,
            error_rate=err,
            ml_result=ml_result,
            service_id="srv-gateway"
        )

        # If risk is elevated, register incident automatically in IncidentManager
        incident_mgr = IncidentManager.get_instance()
        incident_mgr.create_incident_from_analysis(analysis, telemetry_point)

        self.latest_telemetry = telemetry_point
        self.latest_analysis = analysis

        # Advance step if running
        if self.state == "running":
            if self.current_step < self.max_steps:
                self.current_step += 1
            else:
                # Wrap or hold at peak
                pass

        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        cfg = SCENARIO_CONFIGS.get(self.scenario, SCENARIO_CONFIGS["normal"])
        
        # Ensure latest telemetry and analysis exist
        if self.latest_telemetry is None or self.latest_analysis is None:
            t_point = TelemetryService.get_instance().get_current_point()
            ml_engine = MLInferenceEngine.get_instance()
            ml_result = ml_engine.predict_single(
                cpu_utilization=t_point["cpu_utilization"],
                memory_utilization=t_point["memory_utilization"],
                disk_utilization=t_point["disk_utilization"],
                network_latency=t_point["network_latency"],
                error_rate=t_point["error_rate"]
            )
            self.latest_telemetry = t_point
            self.latest_analysis = generate_root_cause_analysis(
                cpu=t_point["cpu_utilization"],
                memory=t_point["memory_utilization"],
                disk=t_point["disk_utilization"],
                latency=t_point["network_latency"],
                error_rate=t_point["error_rate"],
                ml_result=ml_result
            )

        prog_pct = round((self.current_step / self.max_steps) * 100.0, 1)

        return {
            "scenario": self.scenario,
            "scenario_display_name": cfg["display_name"],
            "description": cfg["description"],
            "state": self.state,
            "step": self.current_step,
            "max_steps": self.max_steps,
            "progress_percent": prog_pct,
            "telemetry": self.latest_telemetry,
            "analysis": self.latest_analysis
        }
