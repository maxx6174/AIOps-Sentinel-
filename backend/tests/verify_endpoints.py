from fastapi.testclient import TestClient
from app.main import app

def verify_all():
    client = TestClient(app)
    
    print("Testing /health ...")
    r = client.get("/health")
    print(r.status_code, r.json())
    assert r.status_code == 200

    print("Testing /api/telemetry/snapshot ...")
    r = client.get("/api/telemetry/snapshot")
    print(r.status_code, "Health:", r.json()["overall_health"])
    assert r.status_code == 200

    print("Testing /api/ml/predict ...")
    r = client.post("/api/ml/predict", json={
        "cpu_utilization": 94.0,
        "memory_utilization": 87.0,
        "disk_utilization": 60.0,
        "network_latency": 320.0,
        "error_rate": 6.5
    })
    print(r.status_code, "Failure prob:", r.json()["failure_probability"])
    assert r.status_code == 200

    print("Testing /api/simulation/control start cpu_overload ...")
    r = client.post("/api/simulation/control", json={"action": "start", "scenario": "cpu_overload"})
    print(r.status_code, "State:", r.json()["state"])
    assert r.status_code == 200

    print("Testing /api/simulation/step ...")
    r = client.post("/api/simulation/step")
    print(r.status_code, "Step:", r.json()["step"])
    assert r.status_code == 200

    print("Testing /api/data/sample-csv ...")
    r = client.get("/api/data/sample-csv")
    print(r.status_code, "Bytes:", len(r.content))
    assert r.status_code == 200

    print(">>> ALL 6 API ENDPOINTS VERIFIED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    verify_all()
