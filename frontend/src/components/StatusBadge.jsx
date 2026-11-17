import React from 'react';

export default function StatusBadge({ status, label }) {
  if (!status) return null;
  const s = String(status).toLowerCase();
  
  let badgeClass = 'badge-info';
  if (['healthy', 'low', 'nominal', 'active', 'resolved'].includes(s)) {
    badgeClass = s === 'active' ? 'badge-warning' : 'badge-healthy';
  } else if (['warning', 'moderate'].includes(s)) {
    badgeClass = 'badge-warning';
  } else if (['critical', 'high', 'failed'].includes(s)) {
    badgeClass = 'badge-critical';
  }

  const displayText = label || status.toUpperCase();

  return (
    <span className={`badge ${badgeClass}`}>
      <span style={{ 
        width: 6, 
        height: 6, 
        borderRadius: '50%', 
        backgroundColor: 'currentColor' 
      }}></span>
      {displayText}
    </span>
  );
}
