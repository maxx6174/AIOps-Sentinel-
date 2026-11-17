import React from 'react';

export default function StatCard({ label, value, unit, description, status, icon: Icon }) {
  let statusColor = 'var(--text-main)';
  if (status === 'critical') statusColor = 'var(--danger)';
  else if (status === 'warning') statusColor = 'var(--warning)';

  return (
    <div className="stat-card">
      <div className="stat-label">
        <span>{label}</span>
        {Icon && <Icon size={16} color="var(--text-subtle)" />}
      </div>
      <div className="stat-value" style={{ color: statusColor }}>
        {value}
        {unit && <span style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-muted)', marginLeft: 4 }}>{unit}</span>}
      </div>
      {description && <div className="stat-desc">{description}</div>}
    </div>
  );
}
