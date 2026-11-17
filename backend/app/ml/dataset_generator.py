import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.config import (
    SYNTHETIC_DATASET_PATH,
    SAMPLE_CSV_PATH,
    FEATURE_COLUMNS
)

def generate_synthetic_telemetry(n_samples: int = 6000, seed: int = 42) -> pd.DataFrame:
    """
    Generates a reproducible, statistically grounded synthetic infrastructure telemetry dataset.
    
    Includes realistic multivariate patterns with natural variance and edge-case noise:
    - Normal operating conditions (~76% of data)
    - Transient benign spikes (noisy workloads that recover) (~6% of data)
    - CPU saturation and thread starvation (~5% of data)
    - Memory leak with garbage collection thrashing (~5% of data)
    - Network degradation and packet drops (~4% of data)
    - Cascading infrastructure collapse (~4% of data)
    """
    np.random.seed(seed)
    
    start_time = datetime(2026, 1, 1, 0, 0, 0)
    timestamps = [start_time + timedelta(minutes=i * 2) for i in range(n_samples)]
    
    # Base normal operational distributions
    cpu = np.random.normal(loc=44.0, scale=12.0, size=n_samples)
    memory = np.random.normal(loc=54.0, scale=10.0, size=n_samples)
    disk = np.random.normal(loc=60.0, scale=8.0, size=n_samples)
    latency = np.random.normal(loc=48.0, scale=18.0, size=n_samples)
    error_rate = np.random.exponential(scale=0.8, size=n_samples)
    
    is_anomaly = np.zeros(n_samples, dtype=int)
    failure_occurred = np.zeros(n_samples, dtype=int)
    failure_type = ["none"] * n_samples

    indices = np.random.permutation(n_samples)
    
    # 1. Benign Transient Spikes (High load but NO failure, tests model specificity/false-positives) (~6%)
    benign_idx = indices[: int(n_samples * 0.06)]
    cpu[benign_idx] = np.random.uniform(72.0, 84.0, size=len(benign_idx))
    latency[benign_idx] += np.random.uniform(40.0, 80.0, size=len(benign_idx))
    # No failure, but might trigger warning
    is_anomaly[benign_idx] = np.random.choice([0, 1], size=len(benign_idx), p=[0.7, 0.3])
    failure_occurred[benign_idx] = 0
    for idx in benign_idx:
        failure_type[idx] = "benign_spike"

    # 2. CPU Saturation and Thread Starvation (~5%)
    cpu_fault_idx = indices[int(n_samples * 0.06): int(n_samples * 0.11)]
    cpu[cpu_fault_idx] = np.random.normal(loc=93.0, scale=3.5, size=len(cpu_fault_idx))
    latency[cpu_fault_idx] += np.random.normal(loc=160.0, scale=40.0, size=len(cpu_fault_idx))
    error_rate[cpu_fault_idx] += np.random.normal(loc=4.5, scale=1.5, size=len(cpu_fault_idx))
    is_anomaly[cpu_fault_idx] = 1
    # 92% failure probability under true saturation
    failure_occurred[cpu_fault_idx] = np.random.choice([1, 0], size=len(cpu_fault_idx), p=[0.93, 0.07])
    for idx in cpu_fault_idx:
        failure_type[idx] = "cpu_exhaustion"

    # 3. Memory Leak & GC Stalls (~5%)
    mem_fault_idx = indices[int(n_samples * 0.11): int(n_samples * 0.16)]
    memory[mem_fault_idx] = np.random.normal(loc=94.0, scale=3.0, size=len(mem_fault_idx))
    cpu[mem_fault_idx] += np.random.normal(loc=25.0, scale=8.0, size=len(mem_fault_idx))
    latency[mem_fault_idx] += np.random.normal(loc=110.0, scale=35.0, size=len(mem_fault_idx))
    error_rate[mem_fault_idx] += np.random.normal(loc=5.0, scale=2.0, size=len(mem_fault_idx))
    is_anomaly[mem_fault_idx] = 1
    failure_occurred[mem_fault_idx] = np.random.choice([1, 0], size=len(mem_fault_idx), p=[0.95, 0.05])
    for idx in mem_fault_idx:
        failure_type[idx] = "memory_leak"

    # 4. Network Degradation / Socket Depletion (~4%)
    net_fault_idx = indices[int(n_samples * 0.16): int(n_samples * 0.20)]
    latency[net_fault_idx] = np.random.normal(loc=380.0, scale=90.0, size=len(net_fault_idx))
    error_rate[net_fault_idx] += np.random.normal(loc=7.5, scale=2.5, size=len(net_fault_idx))
    is_anomaly[net_fault_idx] = 1
    failure_occurred[net_fault_idx] = np.random.choice([1, 0], size=len(net_fault_idx), p=[0.91, 0.09])
    for idx in net_fault_idx:
        failure_type[idx] = "network_partition"

    # 5. Cascading Multi-Resource Collapse (~4%)
    cascade_idx = indices[int(n_samples * 0.20): int(n_samples * 0.24)]
    cpu[cascade_idx] = np.random.normal(loc=96.0, scale=2.5, size=len(cascade_idx))
    memory[cascade_idx] = np.random.normal(loc=95.0, scale=2.5, size=len(cascade_idx))
    disk[cascade_idx] = np.random.normal(loc=92.0, scale=4.0, size=len(cascade_idx))
    latency[cascade_idx] = np.random.normal(loc=520.0, scale=110.0, size=len(cascade_idx))
    error_rate[cascade_idx] = np.random.normal(loc=14.0, scale=3.5, size=len(cascade_idx))
    is_anomaly[cascade_idx] = 1
    failure_occurred[cascade_idx] = 1
    for idx in cascade_idx:
        failure_type[idx] = "cascading_failure"

    # Background ambient noise on all series
    cpu += np.random.normal(0, 1.5, size=n_samples)
    memory += np.random.normal(0, 1.2, size=n_samples)
    disk += np.random.normal(0, 0.8, size=n_samples)
    latency += np.random.normal(0, 3.0, size=n_samples)

    # Clip values to physically realistic system limits
    cpu = np.clip(cpu, 2.0, 99.8)
    memory = np.clip(memory, 5.0, 99.8)
    disk = np.clip(disk, 10.0, 99.8)
    latency = np.clip(latency, 8.0, 1500.0)
    error_rate = np.clip(error_rate, 0.0, 95.0)

    df = pd.DataFrame({
        "timestamp": [ts.isoformat() for ts in timestamps],
        "cpu_utilization": np.round(cpu, 2),
        "memory_utilization": np.round(memory, 2),
        "disk_utilization": np.round(disk, 2),
        "network_latency": np.round(latency, 2),
        "error_rate": np.round(error_rate, 2),
        "is_anomaly": is_anomaly,
        "failure_occurred": failure_occurred,
        "failure_type": failure_type
    })

    return df

def save_default_datasets():
    """Generates and writes training dataset and sample evaluation CSV to disk."""
    df = generate_synthetic_telemetry(n_samples=6000, seed=42)
    SYNTHETIC_DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SYNTHETIC_DATASET_PATH, index=False)
    
    # Create realistic sample CSV with 120 rows for judges/users to upload in Data & Reports
    sample_df = generate_synthetic_telemetry(n_samples=120, seed=101)
    upload_sample = sample_df[["timestamp"] + FEATURE_COLUMNS]
    upload_sample.to_csv(SAMPLE_CSV_PATH, index=False)
    
    return SYNTHETIC_DATASET_PATH, SAMPLE_CSV_PATH

if __name__ == "__main__":
    train_path, sample_path = save_default_datasets()
    print(f"Generated synthetic training dataset at {train_path}")
    print(f"Generated sample upload CSV at {sample_path}")
