import React from 'react';
import StatusBadge from './StatusBadge';
import { BarChart3, RefreshCw } from 'lucide-react';

export default function Header({ 
  title, 
  subtitle, 
  overallHealth, 
  riskScore, 
  onRefresh, 
  isRefreshing,
  onOpenModelModal 
}) {
  return (
    <header className="top-header">
      <div className="page-title-box">
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>

      <div className="header-actions">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Health:</span>
          <StatusBadge status={overallHealth} />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingLeft: 12, borderLeft: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Risk Score:</span>
          <span className="font-mono" style={{ 
            fontWeight: 700, 
            fontSize: '0.95rem',
            color: riskScore > 65 ? 'var(--danger)' : riskScore > 35 ? 'var(--warning)' : 'var(--success)'
          }}>
            {riskScore}/100
          </span>
        </div>

        <button 
          className="btn btn-secondary btn-sm" 
          onClick={onOpenModelModal}
          title="Inspect ML Model Metrics & Validation"
        >
          <BarChart3 size={15} />
          <span>ML Benchmarks</span>
        </button>

        <button 
          className="btn btn-secondary btn-sm" 
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Refresh Data"
        >
          <RefreshCw size={14} className={isRefreshing ? 'spin-anim' : ''} />
          <span>{isRefreshing ? 'Refreshing...' : 'Sync'}</span>
        </button>
      </div>
    </header>
  );
}
