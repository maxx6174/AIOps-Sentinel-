import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["project"], "AIOps Sentinel")
        self.assertEqual(data["status"], "operational")

    def test_health_endpoint(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertTrue(data["ml_engine_loaded"])

    def test_telemetry_snapshot(self):
        res = self.client.get("/api/telemetry/snapshot")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("current", data)
        self.assertIn("history", data)
        self.assertIn("services", data)
        self.assertEqual(data["total_services"], 5)

    def test_ml_predict_nominal(self):
        payload = {
            "cpu_utilization": 42.0,
            "memory_utilization": 54.0,
            "disk_utilization": 59.0,
            "network_latency": 45.0,
            "error_rate": 0.5
        }
        res = self.client.post("/api/ml/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["failure_predicted"])
        self.assertEqual(data["risk_level"], "Low")
        self.assertIn("explanation", data)

    def test_ml_predict_failure(self):
        payload = {
            "cpu_utilization": 97.0,
            "memory_utilization": 89.0,
            "disk_utilization": 60.0,
            "network_latency": 320.0,
            "error_rate": 8.0
        }
        res = self.client.post("/api/ml/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["failure_predicted"])
        self.assertIn(data["risk_level"], ["High", "Critical"])
        self.assertIn("Cascading", data["explanation"]["probable_root_cause"])

    def test_ml_metrics_comparison(self):
        res = self.client.get("/api/ml/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("models", data)
        self.assertEqual(len(data["models"]), 3)
        # Check RF metrics
        rf = data["models"][0]
        self.assertGreater(rf["accuracy"], 0.90)
        self.assertGreater(rf["f1_score"], 0.90)

    def test_simulation_scenarios_and_control(self):
        # 1. Check scenarios
        sc_res = self.client.get("/api/simulation/scenarios")
        self.assertEqual(sc_res.status_code, 200)
        scenarios = sc_res.json()
        self.assertEqual(len(scenarios), 5)

        # 2. Start CPU Overload
        ctrl_res = self.client.post("/api/simulation/control", json={"action": "start", "scenario": "cpu_overload"})
        self.assertEqual(ctrl_res.status_code, 200)
        data = ctrl_res.json()
        self.assertEqual(data["scenario"], "cpu_overload")
        self.assertEqual(data["state"], "running")

        # 3. Advance step
        step_res = self.client.post("/api/simulation/step")
        self.assertEqual(step_res.status_code, 200)
        step_data = step_res.json()
        self.assertGreaterEqual(step_data["step"], 1)

        # 4. Pause
        pause_res = self.client.post("/api/simulation/control", json={"action": "pause"})
        self.assertEqual(pause_res.status_code, 200)
        self.assertEqual(pause_res.json()["state"], "paused")

        # 5. Reset
        reset_res = self.client.post("/api/simulation/control", json={"action": "reset"})
        self.assertEqual(reset_res.status_code, 200)
        self.assertEqual(reset_res.json()["state"], "stopped")

    def test_incidents_list(self):
        res = self.client.get("/api/incidents")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("incidents", data)
        self.assertGreater(len(data["incidents"]), 0)

    def test_sample_csv_download(self):
        res = self.client.get("/api/data/sample-csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("cpu_utilization", res.text)
        self.assertIn("network_latency", res.text)

if __name__ == "__main__":
    unittest.main()
