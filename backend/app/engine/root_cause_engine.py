import uuid
from datetime import datetime
from typing import Dict, Any, List
from app.config import METRIC_BASELINES

def generate_root_cause_analysis(
    cpu: float,
    memory: float,
    disk: float,
    latency: float,
    error_rate: float,
    ml_result: Dict[str, Any],
    service_id: str = "srv-gateway",
    incident_id: str = None
) -> Dict[str, Any]:
    """
    Generates structured Explainable AI (XAI) and Root Cause Analysis (RCA).
    
    Adheres strictly to the 4 core investigative questions:
    1. What is happening in the infrastructure?
    2. Why is the abnormal behaviour occurring?
    3. What could happen next?
    4. What action should be taken?
    
    Clearly separates verifiable empirical EVIDENCE from algorithmic HYPOTHESES.
    """
    if not incident_id:
        incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risk_level = ml_result["risk_level"]
    failure_prob = ml_result["failure_probability"]
    anomaly_detected = ml_result["anomaly_detected"]
    anomaly_score = ml_result["anomaly_score"]
    failure_predicted = ml_result["failure_predicted"]
    contributions = ml_result["contributions"]

    # 1. Gather empirical evidence (facts observed directly in telemetry)
    supporting_evidence: List[str] = []
    anomalous_metrics: List[str] = []

    for c in contributions:
        metric_name = c["metric"].replace("_", " ").title()
        val = c["observed_value"]
        unit = c["unit"]
        base = c["baseline_value"]
        pct_dev = c["deviation_percent"]
        status = c["status"]

        if status in ("CRITICAL", "WARNING"):
            anomalous_metrics.append(metric_name)
            direction = "elevated" if pct_dev > 0 else "depressed"
            evidence_str = (
                f"{metric_name} is observed at {val}{unit} ({abs(pct_dev)}% {direction} "
                f"from baseline {base}{unit}, exceeding {status.lower()} threshold)."
            )
            supporting_evidence.append(evidence_str)

    if not supporting_evidence:
        supporting_evidence.append("All primary infrastructure telemetry indicators remain within nominal baseline thresholds.")

    # 2. Formulate algorithmic hypotheses and determine probable root cause
    hypotheses: List[str] = []
    probable_root_cause: str = ""
    recommended_actions: List[str] = []
    
    # 4 questions containers
    what_happening: str = ""
    why_occurring: str = ""
    what_next: str = ""
    what_action: str = ""

    # Signature evaluation based on multi-variate telemetry
    is_cpu_high = cpu >= METRIC_BASELINES["cpu_utilization"]["warning"]
    is_mem_high = memory >= METRIC_BASELINES["memory_utilization"]["warning"]
    is_lat_high = latency >= METRIC_BASELINES["network_latency"]["warning"]
    is_err_high = error_rate >= METRIC_BASELINES["error_rate"]["warning"]
    is_disk_high = disk >= METRIC_BASELINES["disk_utilization"]["warning"]

    if is_cpu_high and is_mem_high and (is_lat_high or is_err_high):
        # Combined / Cascading Failure
        probable_root_cause = "Cascading Resource Exhaustion & System Saturation"
        hypotheses = [
            "Severe concurrent compute and memory contention causing kernel thread context thrashing.",
            "Upstream traffic surge exceeding gateway throughput capacity, creating unhandled request queues.",
            "Backend database connection starvation propagating synchronous request timeouts."
        ]
        what_happening = (
            f"Infrastructure health is critical. CPU ({cpu}%) and Memory ({memory}%) are heavily saturated, "
            f"coinciding with latency spike ({latency} ms) and HTTP error rate surging to {error_rate}%."
        )
        why_occurring = (
            "Multi-tiered resource saturation where compute execution units and JVM/V8 memory pools "
            "have exhausted headroom, triggering synchronous blocking throughout the microservice mesh."
        )
        what_next = (
            f"Immediate service blackout or node crash predicted with {int(failure_prob * 100)}% probability. "
            "Kubernetes liveness probes will fail, triggering cascading pod restarts and user-facing outage."
        )
        recommended_actions = [
            "Trigger automated horizontal pod autoscaling (HPA) to shed load across redundant replicas.",
            "Enable rate-limiting and circuit breakers at the API Gateway to drop non-critical background traffic.",
            "Capture heap and CPU thread dump for deep forensic profiling before restarting degraded pods."
        ]

    elif is_cpu_high and not is_mem_high:
        # CPU Overload
        probable_root_cause = "Compute Saturation / Runaway Worker Execution"
        hypotheses = [
            "Algorithmic bottleneck, unindexed database query serialization, or runaway regex/cryptographic loop.",
            "Sudden spike in cryptographic token validation or unoptimized batch processing payloads.",
            "Thread pool exhaustion in edge ingress handlers starving asynchronous I/O loops."
        ]
        what_happening = (
            f"Sustained CPU compute saturation observed at {cpu}%, while memory utilization ({memory}%) "
            f"remains within operational boundaries."
        )
        why_occurring = (
            "Worker processes or thread pools are consuming 100% of available CPU clock cycles without releasing control, "
            "delaying request event scheduling."
        )
        what_next = (
            f"Application throughput degradation with failure probability of {int(failure_prob * 100)}%. "
            "Incoming HTTP requests will begin timing out, raising HTTP 504 Gateway Timeouts."
        )
        recommended_actions = [
            "Inspect high-utilization thread traces (`top -H`, `py-spy`, or JVM thread dump) to isolate offending thread IDs.",
            "Scale horizontal replica count for CPU-bound worker instances.",
            "Temporarily throttle non-essential cron and asynchronous batch worker jobs."
        ]

    elif is_mem_high and not is_cpu_high:
        # Memory Leak
        probable_root_cause = "Unbounded Memory Accumulation / Memory Leak"
        hypotheses = [
            "Unbounded in-memory caching or retaining references in global collections without eviction.",
            "Persistent session state accumulation or unreleased database cursor connections.",
            "Severe garbage collection pause cycles (stop-the-world) consuming compute during heap sweeps."
        ]
        what_happening = (
            f"Progressive memory retention detected at {memory}%, approaching physical container quota "
            f"while baseline disk usage is {disk}%."
        )
        why_occurring = (
            "Objects are allocated dynamically but never released or garbage collected, steadily depleting available RSS memory."
        )
        what_next = (
            f"Kernel Out-Of-Memory (OOM) Killer invocation predicted with {int(failure_prob * 100)}% probability, "
            "which will abruptly terminate the container process (SIGKILL, exit code 137)."
        )
        recommended_actions = [
            "Initiate rolling zero-downtime container recycle before OOM killer triggers ungraceful termination.",
            "Trigger on-demand heap profiling (V8 memory snapshot or jmap dump) to identify retaining roots.",
            "Audit LRU cache configurations and ensure explicit TTL timeouts on all session stores."
        ]

    elif is_lat_high and not is_cpu_high and not is_mem_high:
        # Network Failure
        probable_root_cause = "Network Transport Degradation / Upstream Latency Anomaly"
        hypotheses = [
            "Upstream network transport layer congestion, inter-VPC packet drop, or routing degradation.",
            "Downstream microservice or database connection pool exhaustion causing synchronous wait times.",
            "DNS resolution latency or TLS handshake negotiation bottlenecks."
        ]
        what_happening = (
            f"Network round-trip latency has jumped to {latency} ms (baseline {METRIC_BASELINES['network_latency']['normal_mean']} ms), "
            f"accompanied by error rate of {error_rate}%."
        )
        why_occurring = (
            "TCP connection backlog or upstream network hops are experiencing high packet retransmission and socket wait times."
        )
        what_next = (
            f"Connection pool exhaustion across consumer clients predicted with {int(failure_prob * 100)}% probability. "
            "Client apps will experience severe lag and disconnects."
        )
        recommended_actions = [
            "Verify egress routes, inter-region peering status, and cloud provider network health status.",
            "Check database and third-party API response time distribution percentiles (p95, p99).",
            "Enable aggressive connection timeouts and circuit breaker fallback responses."
        ]

    elif is_err_high:
        # Error Rate Spike
        probable_root_cause = "Application Layer Fault / High Error Density"
        hypotheses = [
            "Recent software deployment or configuration change introducing unhandled exceptions or 5xx responses.",
            "Authentication token expiration or external third-party API provider outage.",
            "Database schema mismatch or failed database migrations."
        ]
        what_happening = (
            f"Application error rate elevated to {error_rate}%, exceeding operational tolerance threshold."
        )
        why_occurring = (
            "Application code or dependent downstream APIs are rejecting client requests with HTTP 5xx / 4xx error payloads."
        )
        what_next = (
            f"User experience degradation with {int(failure_prob * 100)}% failure likelihood. SLA breach imminent."
        )
        recommended_actions = [
            "Inspect real-time application error logs (`tail -f` / Datadog / Sentry) for unhandled stack traces.",
            "Consider immediate blue/green rollback to the previous stable release artifact.",
            "Validate status of third-party payment and identity upstream dependencies."
        ]

    else:
        # Normal or Benign state
        probable_root_cause = "Normal System Operation (Nominal State)"
        hypotheses = [
            "Infrastructure metrics exhibit expected Gaussian variance consistent with nominal workloads.",
            "No resource saturation or failure signatures detected by machine learning models."
        ]
        what_happening = (
            f"All infrastructure metrics are operating within healthy parameters. "
            f"CPU: {cpu}%, Memory: {memory}%, Latency: {latency} ms, Error Rate: {error_rate}%."
        )
        why_occurring = (
            "Current user traffic and background computational demands are well within allocated cluster capacity."
        )
        what_next = (
            f"Infrastructure is projected to remain stable with high availability. Failure probability is minimal ({int(failure_prob * 100)}%)."
        )
        recommended_actions = [
            "Maintain continuous telemetry ingestion and automated anomaly scanning.",
            "Ensure monitoring alert thresholds remain tuned to seasonal traffic peaks."
        ]

    return {
        "incident_id": incident_id,
        "timestamp": timestamp,
        "risk_level": risk_level,
        "failure_probability": failure_prob,
        "failure_predicted": failure_predicted,
        "anomaly_detected": anomaly_detected,
        "anomaly_score": anomaly_score,
        "contributing_factors": contributions,
        "supporting_evidence": supporting_evidence,
        "hypotheses": hypotheses,
        "probable_root_cause": probable_root_cause,
        "recommended_actions": recommended_actions,
        "four_questions": {
            "what_is_happening": what_happening,
            "why_is_it_occurring": why_occurring,
            "what_could_happen_next": what_next,
            "what_action_should_be_taken": " | ".join(recommended_actions)
        }
    }
