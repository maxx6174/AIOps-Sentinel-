import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  FastForward, 
  Activity, 
  Cpu, 
  Server, 
  Wifi, 
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  Sliders,
  ShieldAlert
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';

export default function SimulationSection({ onSimulationUpdate }) {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState('normal');
  const [simState, setSimState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [simHistory, setSimHistory] = useState([]);

  const isRunningRef = useRef(false);
  const timerRef = useRef(null);

  // Load scenarios on mount
  useEffect(() => {
    async function loadScenarios() {
      try {
        const scList = await api.getSimulationScenarios();
        setScenarios(scList);
        const status = await api.getSimulationStatus();
        setSimState(status);
        setSelectedScenario(status.scenario);
      } catch (err) {
        console.error('Failed to load scenarios:', err);
      }
    }
    loadScenarios();

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Continuous tick loop when running
  useEffect(() => {
    if (simState?.state === 'running') {
      isRunningRef.current = true;
      if (!timerRef.current) {
        timerRef.current = setInterval(async () => {
          try {
            const nextStatus = await api.stepSimulation();
            setSimState(nextStatus);
            if (nextStatus.telemetry) {
              setSimHistory(prev => {
                const updated = [...prev, nextStatus.telemetry];
                return updated.slice(-30);
              });
            }
            if (onSimulationUpdate) onSimulationUpdate();
          } catch (e) {
            console.error('Tick error:', e);
          }
        }, 1200); // Step every 1.2s for smooth visible live demonstration
      }
    } else {
      isRunningRef.current = false;
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [simState?.state]);

  const handleControl = async (action) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.controlSimulation(action, selectedScenario);
      setSimState(res);
      if (action === 'reset') {
        setSimHistory([]);
      }
      if (onSimulationUpdate) onSimulationUpdate();
    } catch (err) {
      setError(err.message || `Simulation ${action} failed`);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectScenario = async (scId) => {
    setSelectedScenario(scId);
    try {
      const res = await api.controlSimulation('start', scId);
      setSimState(res);
      setSimHistory([]);
      if (onSimulationUpdate) onSimulationUpdate();
    } catch (err) {
      setError(err.message);
    }
  };

  const telemetry = simState?.telemetry;
  const analysis = simState?.analysis;
  const fourQ = analysis?.four_questions;

  return (
    <div>
      {/* Scenario Selector Ribbon */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div>
            <div className="card-title">Select Failure Demonstration Scenario</div>
            <div className="card-subtitle">5 isolated failure patterns that execute the actual Python ML pipeline</div>
          </div>
          <span className="code-pill">University Demo Scenarios</span>
        </div>

        <div className="grid-5" style={{ gap: 12 }}>
          {scenarios.map((sc) => {
            const isSelected = selectedScenario === sc.id;
            return (
              <button
                key={sc.id}
                onClick={() => handleSelectScenario(sc.id)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-md)',
                  border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                  backgroundColor: isSelected ? 'var(--primary-light)' : 'var(--bg-surface)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ 
                  fontWeight: 600, 
                  fontSize: '0.85rem', 
                  color: isSelected ? 'var(--primary)' : 'var(--text-main)',
                  marginBottom: 4 
                }}>
                  {sc.display_name}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: 1.3 }}>
                  {sc.description.slice(0, 68)}...
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Control Toolbar & Live Status Bar */}
      <div className="card" style={{ marginBottom: 24, padding: '18px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ display: 'flex', gap: 8 }}>
              {simState?.state === 'running' ? (
                <button className="btn btn-secondary btn-sm" onClick={() => handleControl('pause')}>
                  <Pause size={14} />
                  <span>Pause</span>
                </button>
              ) : (
                <button className="btn btn-primary btn-sm" onClick={() => handleControl('start')}>
                  <Play size={14} />
                  <span>{simState?.step > 0 ? 'Resume' : 'Start Simulation'}</span>
                </button>
              )}

              <button className="btn btn-secondary btn-sm" onClick={() => handleControl('reset')}>
                <RotateCcw size={14} />
                <span>Reset Baseline</span>
              </button>

              <button className="btn btn-secondary btn-sm" onClick={() => handleControl('step')} disabled={simState?.state === 'running'}>
                <FastForward size={14} />
                <span>Single Tick</span>
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingLeft: 16, borderLeft: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Simulation State:</span>
              <span className="code-pill" style={{ 
                fontWeight: 600, 
                color: simState?.state === 'running' ? 'var(--primary)' : 'var(--text-muted)' 
              }}>
                {simState?.state?.toUpperCase()}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            <div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Progress: </span>
              <strong className="font-mono" style={{ fontSize: '0.85rem' }}>Step {simState?.step || 0} / {simState?.max_steps || 30}</strong>
            </div>

            <div style={{ width: 140 }}>
              <div className="risk-meter" style={{ margin: 0 }}>
                <div 
                  className="risk-fill" 
                  style={{ 
                    width: `${simState?.progress_percent || 0}%`, 
                    backgroundColor: 'var(--primary)' 
                  }} 
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', padding: 14, borderRadius: 8, marginBottom: 20 }}>
          {error}
        </div>
      )}

      {/* Live Telemetry Metric Gauges */}
      {telemetry && (
        <div className="grid-5" style={{ marginBottom: 24 }}>
          <div className="stat-card">
            <div className="stat-label">CPU Usage <Cpu size={14} /></div>
            <div className="stat-value font-mono" style={{ 
              color: telemetry.cpu_utilization > 85 ? 'var(--danger)' : telemetry.cpu_utilization > 70 ? 'var(--warning)' : 'var(--text-main)' 
            }}>
              {telemetry.cpu_utilization}%
            </div>
            <div className="stat-desc">Baseline: 42.0%</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Memory Usage <Server size={14} /></div>
            <div className="stat-value font-mono" style={{ 
              color: telemetry.memory_utilization > 88 ? 'var(--danger)' : telemetry.memory_utilization > 75 ? 'var(--warning)' : 'var(--text-main)' 
            }}>
              {telemetry.memory_utilization}%
            </div>
            <div className="stat-desc">Baseline: 55.0%</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Network Latency <Wifi size={14} /></div>
            <div className="stat-value font-mono" style={{ 
              color: telemetry.network_latency > 250 ? 'var(--danger)' : telemetry.network_latency > 120 ? 'var(--warning)' : 'var(--text-main)' 
            }}>
              {telemetry.network_latency} ms
            </div>
            <div className="stat-desc">Baseline: 45.0 ms</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">HTTP Error Rate <AlertTriangle size={14} /></div>
            <div className="stat-value font-mono" style={{ 
              color: telemetry.error_rate > 5.0 ? 'var(--danger)' : telemetry.error_rate > 2.5 ? 'var(--warning)' : 'var(--text-main)' 
            }}>
              {telemetry.error_rate}%
            </div>
            <div className="stat-desc">Baseline: &lt; 1.0%</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Failure Probability</div>
            <div className="stat-value font-mono" style={{ 
              color: analysis?.failure_probability > 0.6 ? 'var(--danger)' : analysis?.failure_probability > 0.3 ? 'var(--warning)' : 'var(--success)' 
            }}>
              {analysis ? `${(analysis.failure_probability * 100).toFixed(1)}%` : '--'}
            </div>
            <div className="stat-desc">Risk: {analysis?.risk_level || 'Normal'}</div>
          </div>
        </div>
      )}

      {/* Live Stream Chart */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div>
            <div className="card-title">Live Dynamic Simulation Telemetry Trajectory</div>
            <div className="card-subtitle">Real-time metric progression emitted by active scenario</div>
          </div>
          <span className="code-pill">Continuous Sampling</span>
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={simHistory} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="timestamp" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#fff', borderColor: '#e2e8f0', borderRadius: 6, fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
              <Line type="monotone" dataKey="cpu_utilization" name="CPU (%)" stroke="#2563eb" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="memory_utilization" name="Memory (%)" stroke="#0891b2" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="error_rate" name="Error Rate (%)" stroke="#ef4444" strokeWidth={1.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Real-time Explainable AI & Live RCA Verdict */}
      {analysis && (
        <div className="grid-2">
          {/* Live 4 Questions Box */}
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">
                  <BrainCircuit size={17} color="var(--primary)" />
                  <span>Real-Time Explainable AI Insights</span>
                </div>
                <div className="card-subtitle">Live inference generated for step {simState.step}</div>
              </div>
              <StatusBadge status={analysis.risk_level} />
            </div>

            {fourQ && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div className="question-box">
                  <div className="question-label">1. What is happening?</div>
                  <div className="question-text">{fourQ.what_is_happening}</div>
                </div>

                <div className="question-box">
                  <div className="question-label">2. Why is abnormal behaviour occurring?</div>
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

          {/* Root Cause & Remediation */}
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">Root Cause Diagnosis & Remediations</div>
                <div className="card-subtitle">Incident ID: {analysis.incident_id}</div>
              </div>
              <span className="code-pill">
                Anomaly: {analysis.anomaly_detected ? 'TRIGGERED' : 'CLEAN'}
              </span>
            </div>

            <div style={{ 
              backgroundColor: 'var(--bg-subtle)', 
              padding: '16px', 
              borderRadius: 'var(--radius-md)',
              marginBottom: 16
            }}>
              <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                Synthesized Root Cause
              </div>
              <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginTop: 4 }}>
                {analysis.probable_root_cause}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: 8 }}>
                Automated Remediation Playbook:
              </div>
              <ul style={{ paddingLeft: 20, fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {analysis.recommended_actions?.map((act, i) => (
                  <li key={i}>{act}</li>
                ))}
              </ul>
            </div>

            <div style={{ marginTop: 20, borderTop: '1px solid var(--border-subtle)', paddingTop: 14 }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
                Empirical Evidence Observed:
              </div>
              <ul style={{ paddingLeft: 18, fontSize: '0.8rem', color: 'var(--text-main)', display: 'flex', flexDirection: 'column', gap: 3 }}>
                {analysis.supporting_evidence?.map((ev, i) => (
                  <li key={i}>{ev}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
