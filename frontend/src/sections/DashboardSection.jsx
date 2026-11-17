import React from 'react';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import { 
  Cpu, 
  HardDrive, 
  Server, 
  Wifi, 
  AlertTriangle, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle,
  Clock,
  ArrowRight
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

export default function DashboardSection({ snapshot, incidents, onNavigate }) {
  if (!snapshot) return null;

  const { current, history, services, overall_health, risk_score, healthy_count, warning_count, critical_count, total_services } = snapshot;

  return (
    <div>
      {/* Top Infrastructure Health Banner */}
      <div className="card" style={{ padding: '20px 24px', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{
              width: 48,
              height: 48,
              borderRadius: 'var(--radius-md)',
              backgroundColor: overall_health === 'CRITICAL' ? 'var(--danger-bg)' : overall_health === 'WARNING' ? 'var(--warning-bg)' : 'var(--success-bg)',
              color: overall_health === 'CRITICAL' ? 'var(--danger)' : overall_health === 'WARNING' ? 'var(--warning)' : 'var(--success)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {overall_health === 'CRITICAL' ? <AlertTriangle size={26} /> : overall_health === 'WARNING' ? <AlertCircle size={26} /> : <ShieldCheck size={26} />}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Infrastructure Health: {overall_health}
                </h2>
                <StatusBadge status={overall_health} />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: 2 }}>
                {total_services} Monitored Microservices &bull; {healthy_count} Healthy, {warning_count} Warning, {critical_count} Critical
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Risk Score</span>
              <div className="font-mono" style={{ 
                fontSize: '1.6rem', 
                fontWeight: 700,
                color: risk_score > 65 ? 'var(--danger)' : risk_score > 35 ? 'var(--warning)' : 'var(--success)'
              }}>
                {risk_score}<span style={{ fontSize: '0.9rem', color: 'var(--text-subtle)' }}>/100</span>
              </div>
            </div>
            <button className="btn btn-primary btn-sm" onClick={() => onNavigate('simulation')}>
              <span>Live Simulation</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* Risk meter bar */}
        <div className="risk-meter" style={{ marginTop: 16 }}>
          <div 
            className="risk-fill" 
            style={{ 
              width: `${risk_score}%`,
              backgroundColor: risk_score > 65 ? 'var(--danger)' : risk_score > 35 ? 'var(--warning)' : 'var(--primary)'
            }}
          />
        </div>
      </div>

      {/* Core Telemetry Stats Grid */}
      <div className="grid-5" style={{ marginBottom: 24 }}>
        <StatCard 
          label="CPU Utilization" 
          value={current.cpu_utilization} 
          unit="%" 
          status={current.cpu_utilization > 85 ? 'critical' : current.cpu_utilization > 70 ? 'warning' : 'normal'}
          description="Normal baseline: ~42%" 
          icon={Cpu} 
        />
        <StatCard 
          label="Memory Utilization" 
          value={current.memory_utilization} 
          unit="%" 
          status={current.memory_utilization > 88 ? 'critical' : current.memory_utilization > 75 ? 'warning' : 'normal'}
          description="Normal baseline: ~55%" 
          icon={Server} 
        />
        <StatCard 
          label="Disk Utilization" 
          value={current.disk_utilization} 
          unit="%" 
          status={current.disk_utilization > 90 ? 'critical' : current.disk_utilization > 80 ? 'warning' : 'normal'}
          description="Normal baseline: ~60%" 
          icon={HardDrive} 
        />
        <StatCard 
          label="Network Latency" 
          value={current.network_latency} 
          unit="ms" 
          status={current.network_latency > 250 ? 'critical' : current.network_latency > 120 ? 'warning' : 'normal'}
          description="Normal baseline: ~45 ms" 
          icon={Wifi} 
        />
        <StatCard 
          label="HTTP Error Rate" 
          value={current.error_rate} 
          unit="%" 
          status={current.error_rate > 5.0 ? 'critical' : current.error_rate > 2.5 ? 'warning' : 'normal'}
          description="Normal baseline: < 1.0%" 
          icon={AlertTriangle} 
        />
      </div>

      {/* Recent Telemetry Time-Series Chart */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Live Infrastructure Telemetry Stream</div>
            <div className="card-subtitle">Real-time rolling metric window (CPU, Memory, Latency)</div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('monitoring')}>
            View Detailed Telemetry
          </button>
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="timestamp" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={[0, 100]} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  borderColor: '#e2e8f0', 
                  borderRadius: 6, 
                  fontSize: 12,
                  boxShadow: '0 2px 4px rgba(0,0,0,0.08)'
                }} 
              />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
              <Line type="monotone" dataKey="cpu_utilization" name="CPU (%)" stroke="#2563eb" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="memory_utilization" name="Memory (%)" stroke="#0891b2" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="disk_utilization" name="Disk (%)" stroke="#64748b" strokeWidth={1.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Grid: Recent Incidents & Monitored Services */}
      <div className="grid-2">
        {/* Recent Incidents Card */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Recent Infrastructure Incidents</div>
              <div className="card-subtitle">Identified anomalies & root cause classifications</div>
            </div>
            <span className="code-pill">{incidents?.length || 0} Total</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {incidents && incidents.length > 0 ? (
              incidents.slice(0, 3).map((inc) => (
                <div 
                  key={inc.id} 
                  style={{ 
                    border: '1px solid var(--border-subtle)', 
                    borderRadius: 'var(--radius-md)', 
                    padding: '12px 16px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 4
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="code-pill" style={{ fontWeight: 600 }}>{inc.id}</span>
                      <StatusBadge status={inc.severity} />
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Clock size={12} />
                      {inc.timestamp.split(' ')[1] || inc.timestamp}
                    </span>
                  </div>
                  <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-main)', marginTop: 2 }}>
                    {inc.title}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Root Cause: {inc.root_cause}
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No active incidents recorded.
              </div>
            )}
          </div>
        </div>

        {/* Monitored Services Summary */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Monitored Service Topology</div>
              <div className="card-subtitle">Real-time status across edge, compute & data layers</div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('monitoring')}>
              Inspect Services
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {services.map((s) => (
              <div 
                key={s.id}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  backgroundColor: 'var(--bg-subtle)',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.85rem'
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{s.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.type} &bull; <code style={{ fontSize: '0.72rem' }}>{s.endpoint}</code></div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ textAlign: 'right', fontSize: '0.78rem' }}>
                    <div className="font-mono">{s.latency} ms</div>
                    <div style={{ color: 'var(--text-subtle)' }}>{s.uptime}% up</div>
                  </div>
                  <StatusBadge status={s.status} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
