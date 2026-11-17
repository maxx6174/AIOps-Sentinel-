import unittest
from app.ml.inference import MLInferenceEngine
from app.engine.telemetry_service import TelemetryService
from app.engine.simulation_engine import SimulationEngine
from app.engine.root_cause_engine import generate_root_cause_analysis
from app.engine.incident_manager import IncidentManager

class TestAIOpsSentinelBackend(unittest.TestCase):
    def setUp(self):
        self.ml_engine = MLInferenceEngine.get_instance()
        self.telemetry_svc = TelemetryService.get_instance()
        self.sim_engine = SimulationEngine.get_instance()
        self.inc_manager = IncidentManager.get_instance()

    def test_ml_inference_nominal(self):
        """Test that nominal parameters produce low failure probability and no anomaly."""
        res = self.ml_engine.predict_single(
            cpu_utilization=40.0,
            memory_utilization=50.0,
            disk_utilization=55.0,
            network_latency=42.0,
            error_rate=0.4
        )
        self.assertFalse(res["failure_predicted"])
        self.assertLess(res["failure_probability"], 0.40)
        self.assertEqual(res["risk_level"], "Low")

    def test_ml_inference_cpu_overload(self):
        """Test that extreme CPU saturation triggers failure prediction and high/critical risk."""
        res = self.ml_engine.predict_single(
            cpu_utilization=98.0,
            memory_utilization=65.0,
            disk_utilization=60.0,
            network_latency=220.0,
            error_rate=5.5
        )
        self.assertTrue(res["failure_predicted"])
        self.assertGreater(res["failure_probability"], 0.70)
        self.assertIn(res["risk_level"], ["High", "Critical"])

    def test_ml_inference_memory_leak(self):
        """Test that memory approaching 98% triggers anomaly and failure risk."""
        res = self.ml_engine.predict_single(
            cpu_utilization=70.0,
            memory_utilization=97.0,
            disk_utilization=62.0,
            network_latency=120.0,
            error_rate=4.2
        )
        self.assertTrue(res["failure_predicted"])
        self.assertTrue(res["anomaly_detected"])

    def test_root_cause_engine_four_questions(self):
        """Verify that XAI answers the 4 core investigative questions."""
        res = self.ml_engine.predict_single(
            cpu_utilization=95.0,
            memory_utilization=92.0,
            disk_utilization=90.0,
            network_latency=450.0,
            error_rate=12.0
        )
        analysis = generate_root_cause_analysis(95.0, 92.0, 90.0, 450.0, 12.0, res)
        four_q = analysis["four_questions"]

        self.assertTrue(len(four_q["what_is_happening"]) > 10)
        self.assertTrue(len(four_q["why_is_it_occurring"]) > 10)
        self.assertTrue(len(four_q["what_could_happen_next"]) > 10)
        self.assertTrue(len(four_q["what_action_should_be_taken"]) > 10)
        self.assertTrue(len(analysis["supporting_evidence"]) > 0)
        self.assertTrue(len(analysis["hypotheses"]) > 0)

    def test_simulation_all_five_scenarios(self):
        """Verify all 5 scenarios start, progress, and generate valid telemetry & predictions."""
        scenarios = ["normal", "cpu_overload", "memory_leak", "network_failure", "combined_failure"]
        for sc in scenarios:
            self.sim_engine.reset()
            status = self.sim_engine.start(sc)
            self.assertEqual(status["scenario"], sc)
            self.assertIn(status["state"], ["running", "paused", "stopped"])
            self.assertIn("telemetry", status)
            self.assertIn("analysis", status)

            # Advance by 5 steps
            for _ in range(5):
                step_status = self.sim_engine.step()
                self.assertIsNotNone(step_status["telemetry"])
                self.assertIsNotNone(step_status["analysis"])

if __name__ == "__main__":
    unittest.main()
