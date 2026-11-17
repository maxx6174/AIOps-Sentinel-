import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import { 
  BrainCircuit, 
  HelpCircle, 
  AlertTriangle, 
  CheckCircle2, 
  Sliders, 
  Activity, 
  Layers,
  ArrowUpRight,
  ShieldAlert
} from 'lucide-react';

export default function AIAnalysisSection({ currentTelemetry, onOpenBenchmarks }) {
  const [cpu, setCpu] = useState(currentTelemetry?.cpu_utilization || 42.0);
  const [memory, setMemory] = useState(currentTelemetry?.memory_utilization || 54.0);
  const [disk, setDisk] = useState(currentTelemetry?.disk_utilization || 59.0);
  const [latency, setLatency] = useState(currentTelemetry?.network_latency || 45.0);
  const [errorRate, setErrorRate] = useState(currentTelemetry?.error_rate || 0.5);

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Sync state if telemetry updates and user hasn't touched
  useEffect(() => {
    if (currentTelemetry && !prediction) {
      runPrediction(
        currentTelemetry.cpu_utilization,
        currentTelemetry.memory_utilization,
        currentTelemetry.disk_utilization,
        currentTelemetry.network_latency,
        currentTelemetry.error_rate
      );
    }
  }, [currentTelemetry]);

  const runPrediction = async (c = cpu, m = memory, d = disk, l = latency, e = errorRate) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.predict({
        cpu_utilization: parseFloat(c),
        memory_utilization: parseFloat(m),
        disk_utilization: parseFloat(d),
        network_latency: parseFloat(l),
        error_rate: parseFloat(e)
      });
      setPrediction(res);
    } catch (err) {
      setError(err.message || 'ML Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyPreset = (preset) => {
    let c = 42, m = 54, d = 59, l = 45, e = 0.5;
    if (preset === 'cpu_spike') {
      c = 96.5; m = 68.0; d = 60.0; l = 220.0; e = 4.2;
    } else if (preset === 'mem_leak') {
      c = 68.0; m = 97.2; d = 65.0; l = 160.0; e = 5.8;
    } else if (preset === 'net_drop') {
      c = 44.0; m = 56.0; d = 59.0; l = 680.0; e = 12.4;
    } else if (preset === 'cascade') {
      c = 98.0; m = 96.0; d = 92.0; l = 740.0; e = 18.5;
    }
    setCpu(c);
    setMemory(m);
    setDisk(d);
    setLatency(l);
    setErrorRate(e);
    runPrediction(c, m, d, l, e);
  };

  const explanation = prediction?.explanation;
  const fourQ = explanation?.four_questions;

  return (
    <div>
      {/* Interactive Telemetry Tuning & ML Evaluation Box */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div>
            <div className="card-title">
              <Sliders size={18} color="var(--primary)" />
              <span>Interactive Model Evaluation Sandbox</span>
            </div>
            <div className="card-subtitle">Adjust telemetry sliders to trigger real-time ML inference & Explainable AI</div>
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button className="btn btn-secondary btn-sm" onClick={() => handleApplyPreset('normal')}>Nominal</button>
            <button className="btn btn-secondary btn-sm" onClick={() => handleApplyPreset('cpu_spike')}>CPU Spike</button>
            <button className="btn btn-secondary btn-sm" onClick={() => handleApplyPreset('mem_leak')}>Memory Leak</button>
            <button className="btn btn-secondary btn-sm" onClick={() => handleApplyPreset('net_drop')}>Network Drop</button>
            <button className="btn btn-secondary btn-sm" onClick={() => handleApplyPreset('cascade')}>Cascading</button>
          </div>
        </div>

        {/* Sliders Grid */}
        <div className="grid-5" style={{ marginBottom: 20 }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
              <span>CPU Usage</span>
              <strong className="font-mono">{cpu}%</strong>
            </div>
            <input 
              type="range" min="5" max="100" step="0.5" value={cpu} 
              onChange={(e) => setCpu(parseFloat(e.target.value))} 
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
              <span>Memory Usage</span>
              <strong className="font-mono">{memory}%</strong>
            </div>
            <input 
              type="range" min="10" max="100" step="0.5" value={memory} 
              onChange={(e) => setMemory(parseFloat(e.target.value))} 
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
              <span>Disk Usage</span>
              <strong className="font-mono">{disk}%</strong>
            </div>
            <input 
              type="range" min="10" max="100" step="0.5" value={disk} 
              onChange={(e) => setDisk(parseFloat(e.target.value))} 
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
              <span>Latency</span>
              <strong className="font-mono">{latency} ms</strong>
            </div>
            <input 
              type="range" min="10" max="1000" step="5" value={latency} 
              onChange={(e) => setLatency(parseFloat(e.target.value))} 
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
              <span>HTTP Error Rate</span>
              <strong className="font-mono">{errorRate}%</strong>
            </div>
            <input 
              type="range" min="0" max="30" step="0.2" value={errorRate} 
              onChange={(e) => setErrorRate(parseFloat(e.target.value))} 
              style={{ width: '100%' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button 
            className="btn btn-primary btn-sm" 
            onClick={() => runPrediction()} 
            disabled={loading}
          >
            <BrainCircuit size={14} />
            <span>{loading ? 'Evaluating ML Pipeline...' : 'Run ML Inference'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', padding: 14, borderRadius: 8, marginBottom: 20 }}>
          {error}
        </div>
      )}

      {prediction && (
        <>
          {/* Top ML Inference Verdict Grid */}
          <div className="grid-4" style={{ marginBottom: 24 }}>
            <div className="stat-card">
              <div className="stat-label">Failure Prediction</div>
              <div className="stat-value" style={{ 
                color: prediction.failure_predicted ? 'var(--danger)' : 'var(--success)',
                fontSize: '1.25rem'
              }}>
                {prediction.failure_predicted ? 'FAILURE PREDICTED' : 'NORMAL / SAFE'}
              </div>
              <div className="stat-desc">Primary Model: Random Forest</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Failure Probability</div>
              <div className="stat-value font-mono">
                {(prediction.failure_probability * 100).toFixed(1)}%
              </div>
              <div className="stat-desc">Baseline (Logistic Reg): {(prediction.logistic_baseline_probability * 100).toFixed(1)}%</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Anomaly Detection</div>
              <div className="stat-value" style={{ 
                color: prediction.anomaly_detected ? 'var(--warning)' : 'var(--success)',
                fontSize: '1.25rem'
              }}>
                {prediction.anomaly_detected ? 'ANOMALY DETECTED' : 'WITHIN BOUNDS'}
              </div>
              <div className="stat-desc">Isolation Forest score: {prediction.anomaly_score}/100</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Risk Classification</div>
              <div style={{ marginTop: 8 }}>
                <StatusBadge status={prediction.risk_level} />
              </div>
              <div className="stat-desc" style={{ marginTop: 8 }}>Incident ID: {prediction.prediction_id}</div>
            </div>
          </div>

          {/* Core Explainability Section: Answers to 4 Investigative Questions */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <div>
                <div className="card-title">
                  <BrainCircuit size={18} color="var(--primary)" />
                  <span>Explainable AI (XAI) &mdash; Four Core Operational Questions</span>
                </div>
                <div className="card-subtitle">Algorithmic answers generated dynamically from telemetry and model decision paths</div>
              </div>
              <button className="btn btn-secondary btn-sm" onClick={onOpenBenchmarks}>
                Model Comparison
              </button>
            </div>

            {fourQ && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                <div className="question-box">
                  <div className="question-label">1. What is happening in the infrastructure?</div>
                  <div className="question-text">{fourQ.what_is_happening}</div>
                </div>

                <div className="question-box">
                  <div className="question-label">2. Why is the abnormal behaviour occurring?</div>
                  <div className="question-text">{fourQ.why_is_it_occurring}</div>
                </div>

                <div className="question-box">
                  <div className="question-label">3. What could happen next?</div>
                  <div className="question-text">{fourQ.what_could_happen_next}</div>
                </div>

                <div className="question-box" style={{ borderLeftColor: 'var(--success)' }}>
                  <div className="question-label" style={{ color: 'var(--success)' }}>4. What action should be taken?</div>
                  <div className="question-text">{fourQ.what_action_should_be_taken}</div>
                </div>
              </div>
            )}
          </div>

          {/* Root Cause, Evidence vs Hypothesis, and Feature Contributions Grid */}
          <div className="grid-2">
            {/* Probable Root Cause & Recommended Remediations */}
            <div className="card">
              <div className="card-header">
                <div>
                  <div className="card-title">Probable Root Cause & Actions</div>
                  <div className="card-subtitle">Synthesized diagnostic conclusion</div>
                </div>
                <StatusBadge status={prediction.risk_level} />
              </div>

              <div style={{ 
                backgroundColor: 'var(--bg-subtle)', 
                padding: '16px', 
                borderRadius: 'var(--radius-md)',
                marginBottom: 16
              }}>
                <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                  Primary Diagnostic Conclusion
                </div>
                <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginTop: 4 }}>
                  {explanation.probable_root_cause}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: 8 }}>
                  Recommended Remediation Steps:
                </div>
                <ul style={{ paddingLeft: 20, fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {explanation.recommended_actions?.map((act, i) => (
                    <li key={i}>{act}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Evidence vs Hypothesis Table */}
            <div className="card">
              <div className="card-header">
                <div>
                  <div className="card-title">Empirical Evidence vs. Hypotheses</div>
                  <div className="card-subtitle">Differentiating measured facts from algorithmic deductions</div>
                </div>
              </div>

              <div style={{ marginBottom: 16 }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', marginBottom: 6 }}>
                  Empirical Evidence (Observed Metrics):
                </div>
                <ul style={{ paddingLeft: 18, fontSize: '0.82rem', color: 'var(--text-main)', display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {explanation.supporting_evidence?.map((ev, i) => (
                    <li key={i}>{ev}</li>
                  ))}
                </ul>
              </div>

              <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 14 }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                  Algorithmic Hypotheses:
                </div>
                <ul style={{ paddingLeft: 18, fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {explanation.hypotheses?.map((hyp, i) => (
                    <li key={i}>{hyp}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Metric Attribution & Local Feature Importance Breakdown */}
          <div className="card" style={{ marginTop: 24 }}>
            <div className="card-header">
              <div>
                <div className="card-title">Local Metric Attribution & Baseline Deviations</div>
                <div className="card-subtitle">How individual telemetry inputs influenced the Random Forest classification</div>
              </div>
            </div>

            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Observed Value</th>
                    <th>Baseline Value</th>
                    <th>Deviation</th>
                    <th>RF Global Importance</th>
                    <th>Local Attribution</th>
                    <th>Metric Status</th>
                  </tr>
                </thead>
                <tbody>
                  {explanation.contributing_factors?.map((f, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, textTransform: 'capitalize' }}>{f.metric.replace('_', ' ')}</td>
                      <td className="font-mono">{f.observed_value} {f.unit}</td>
                      <td className="font-mono" style={{ color: 'var(--text-muted)' }}>{f.baseline_value} {f.unit}</td>
                      <td className="font-mono" style={{ 
                        color: f.deviation_percent > 30 ? 'var(--danger)' : f.deviation_percent > 15 ? 'var(--warning)' : 'var(--text-muted)' 
                      }}>
                        {f.deviation_percent > 0 ? `+${f.deviation_percent}%` : `${f.deviation_percent}%`}
                      </td>
                      <td className="font-mono">{(f.importance_score * 100).toFixed(1)}%</td>
                      <td className="font-mono" style={{ fontWeight: 600, color: 'var(--primary)' }}>
                        {(f.local_impact * 100).toFixed(1)}%
                      </td>
                      <td><StatusBadge status={f.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
