import React from 'react';
import { 
  LayoutDashboard, 
  Activity, 
  BrainCircuit, 
  PlayCircle, 
  FileSpreadsheet, 
  ShieldCheck 
} from 'lucide-react';

const SECTIONS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'monitoring', label: 'Infrastructure', icon: Activity },
  { id: 'ai-analysis', label: 'AI Analysis', icon: BrainCircuit },
  { id: 'simulation', label: 'Live Simulation', icon: PlayCircle },
  { id: 'data-reports', label: 'Data & Reports', icon: FileSpreadsheet },
];

export default function Sidebar({ activeSection, onSelectSection }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">
          <ShieldCheck size={20} strokeWidth={2.5} />
        </div>
        <div>
          <div className="sidebar-title">AIOps Sentinel</div>
          <div className="sidebar-subtitle">Infrastructure AI</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {SECTIONS.map((sec) => {
          const Icon = sec.icon;
          const isActive = activeSection === sec.id;
          return (
            <button
              key={sec.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelectSection(sec.id)}
            >
              <Icon size={18} strokeWidth={isActive ? 2.2 : 1.8} />
              <span>{sec.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <p style={{ fontWeight: 600, color: 'var(--text-muted)' }}>Vel Tech Project Demo</p>
        <p style={{ marginTop: 2 }}>v1.0.0 &bull; Explainable ML</p>
      </div>
    </aside>
  );
}
