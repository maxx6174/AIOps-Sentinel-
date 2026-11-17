import time
import threading
import requests
import uvicorn
from app.main import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="warning")

def run_integration_tests():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Give server time to bind

    base_url = "http://127.0.0.1:8888"

    print("--- 1. Testing Root and Health Endpoints ---")
    r = requests.get(f"{base_url}/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    health_data = r.json()
    assert health_data["status"] == "HEALTHY"
    print(f"Health check OK: {health_data}")

    print("--- 2. Testing Telemetry Snapshot ---")
    r = requests.get(f"{base_url}/api/telemetry/snapshot")
    assert r.status_code == 200, f"Snapshot failed: {r.text}"
    snap = r.json()
    assert "current" in snap and "history" in snap
    assert snap["total_services"] == 5
    print(f"Snapshot OK: Health={snap['overall_health']}, Services={snap['total_services']}")

    print("--- 3. Testing ML Prediction Endpoint ---")
    payload = {
        "cpu_utilization": 96.0,
        "memory_utilization": 65.0,
        "disk_utilization": 60.0,
        "network_latency": 250.0,
        "error_rate": 5.0
    }
    r = requests.post(f"{base_url}/api/ml/predict", json=payload)
    assert r.status_code == 200, f"Prediction failed: {r.text}"
    pred = r.json()
    assert pred["failure_predicted"] is True
    assert "four_questions" in pred["explanation"]
    print(f"Prediction OK: Prob={pred['failure_probability']}, Risk={pred['risk_level']}")
    print(f"RCA: {pred['explanation']['probable_root_cause']}")

    print("--- 4. Testing Simulation Controls across 5 Scenarios ---")
    scenarios = ["normal", "cpu_overload", "memory_leak", "network_failure", "combined_failure"]
    for sc in scenarios:
        r = requests.post(f"{base_url}/api/simulation/control", json={"action": "start", "scenario": sc})
        assert r.status_code == 200, f"Simulation start failed for {sc}: {r.text}"
        sim = r.json()
        assert sim["scenario"] == sc
        assert sim["state"] == "running"
        print(f"Scenario '{sc}' initialized successfully.")

    print("--- 5. Testing Simulation Step Tick ---")
    r = requests.post(f"{base_url}/api/simulation/step")
    assert r.status_code == 200
    stepped = r.json()
    assert stepped["step"] >= 1
    print(f"Simulation step advanced to step {stepped['step']}.")

    print("--- 6. Testing Model Benchmarks Endpoint ---")
    r = requests.get(f"{base_url}/api/ml/metrics")
    assert r.status_code == 200
    metrics = r.json()
    assert len(metrics["models"]) == 3
    print("Model benchmarks OK: Models verified (RF, LR, Isolation Forest).")

    print("--- 7. Testing Sample CSV Download ---")
    r = requests.get(f"{base_url}/api/data/sample-csv")
    assert r.status_code == 200
    assert "cpu_utilization" in r.text
    print(f"Sample CSV download OK: {len(r.text)} bytes.")

    print("\n=======================================================")
    print(">>> ALL BACKEND API INTEGRATION TESTS PASSED 100%! <<<")
    print("=======================================================")

if __name__ == "__main__":
    run_integration_tests()
