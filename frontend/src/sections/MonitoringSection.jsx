import React, { useState } from 'react';
import StatusBadge from '../components/StatusBadge';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';
import { Cpu, Server, Wifi, AlertTriangle, HardDrive, RefreshCw } from 'lucide-react';

export default function MonitoringSection({ snapshot, onRefresh, isRefreshing }) {
  const [selectedMetric, setSelectedMetric] = useState('all');

  if (!snapshot) return null;
  const { current, history, services } = snapshot;

  return (
    <div>
      {/* Metric Selector Tabs */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {[
            { id: 'all', label: 'Overview All' },
            { id: 'compute', label: 'CPU & Memory' },
            { id: 'network', label: 'Network Latency' },
            { id: 'error', label: 'HTTP Error Rate' }
          ].map(tab => (
            <button
              key={tab.id}
              className={`btn ${selectedMetric === tab.id ? 'btn-primary' : 'btn-secondary'} btn-sm`}
              onClick={() => setSelectedMetric(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <button className="btn btn-secondary btn-sm" onClick={onRefresh} disabled={isRefreshing}>
          <RefreshCw size={13} className={isRefreshing ? 'spin-anim' : ''} />
          <span>Sync Telemetry</span>
        </button>
      </div>

      {/* Main Metric Visualizer Chart */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div>
            <div className="card-title">Infrastructure Time-Series Diagnostics</div>
            <div className="card-subtitle">Continuous historical stream sampled at 3-second intervals</div>
          </div>
          <div style={{ display: 'flex', gap: 16, fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            <span>CPU: <strong className="font-mono">{current.cpu_utilization}%</strong></span>
            <span>Mem: <strong className="font-mono">{current.memory_utilization}%</strong></span>
            <span>Lat: <strong className="font-mono">{current.network_latency} ms</strong></span>
          </div>
        </div>

        <div style={{ height: 320, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            {selectedMetric === 'network' ? (
              <AreaChart data={history} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="timestamp" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#fff', borderColor: '#e2e8f0', borderRadius: 6, fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
                <Area type="monotone" dataKey="network_latency" name="Network Latency (ms)" stroke="#8b5cf6" fill="#ede9fe" strokeWidth={2} />
              </AreaChart>
            ) : selectedMetric === 'error' ? (
              <AreaChart data={history} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="timestamp" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#fff', borderColor: '#e2e8f0', borderRadius: 6, fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
                <Area type="monotone" dataKey="error_rate" name="HTTP Error Rate (%)" stroke="#ef4444" fill="#fee2e2" strokeWidth={2} />
              </AreaChart>
            ) : (
              <LineChart data={history} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="timestamp" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#fff', borderColor: '#e2e8f0', borderRadius: 6, fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
                <Line type="monotone" dataKey="cpu_utilization" name="CPU Usage (%)" stroke="#2563eb" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="memory_utilization" name="Memory Usage (%)" stroke="#0891b2" strokeWidth={2} dot={false} />
                {selectedMetric === 'all' && (
                  <Line type="monotone" dataKey="disk_utilization" name="Disk (%)" stroke="#64748b" strokeWidth={1.5} dot={false} />
                )}
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      {/* Granular Microservice Health Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Live Microservice Registry & Telemetry</div>
            <div className="card-subtitle">Granular health metrics, operational latencies and error rates per node</div>
          </div>
          <span className="code-pill">5 Nodes Monitored</span>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Service ID</th>
                <th>Service Name</th>
                <th>Layer / Type</th>
                <th>Target Endpoint</th>
                <th>Health Status</th>
                <th>Latency</th>
                <th>Error Rate</th>
                <th>Availability</th>
              </tr>
            </thead>
            <tbody>
              {services.map((s) => (
                <tr key={s.id}>
                  <td className="code-pill" style={{ fontSize: '0.75rem' }}>{s.id}</td>
                  <td style={{ fontWeight: 600 }}>{s.name}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{s.type}</td>
                  <td><code style={{ fontSize: '0.78rem' }}>{s.endpoint}</code></td>
                  <td><StatusBadge status={s.status} /></td>
                  <td className="font-mono">{s.latency} ms</td>
                  <td className="font-mono">{s.error_rate}%</td>
                  <td className="font-mono" style={{ color: 'var(--success)', fontWeight: 600 }}>{s.uptime}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
