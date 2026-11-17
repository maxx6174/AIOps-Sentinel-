import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ModelComparisonModal from './components/ModelComparisonModal';

import DashboardSection from './sections/DashboardSection';
import MonitoringSection from './sections/MonitoringSection';
import AIAnalysisSection from './sections/AIAnalysisSection';
import SimulationSection from './sections/SimulationSection';
import DataReportsSection from './sections/DataReportsSection';

import { api } from './api/client';

export default function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [snapshot, setSnapshot] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isModelModalOpen, setIsModelModalOpen] = useState(false);
  const [error, setError] = useState(null);

  const fetchGlobalData = async () => {
    try {
      setIsRefreshing(true);
      setError(null);
      const [snapData, incData] = await Promise.all([
        api.getTelemetrySnapshot(),
        api.getIncidents()
      ]);
      setSnapshot(snapData);
      setIncidents(incData.incidents || []);
    } catch (err) {
      console.error('Failed to sync telemetry:', err);
      setError('Backend communication offline. Ensure backend is running on http://127.0.0.1:8000');
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchGlobalData();

    // Auto-refresh telemetry every 3.5 seconds
    const interval = setInterval(() => {
      // Don't auto-poll if user is in deep simulation or uploading
      if (activeSection === 'dashboard' || activeSection === 'monitoring') {
        api.getTelemetrySnapshot()
          .then(data => setSnapshot(data))
          .catch(() => {});
      }
    }, 3500);

    return () => clearInterval(interval);
  }, [activeSection]);

  const getSectionTitle = () => {
    switch (activeSection) {
      case 'dashboard':
        return {
          title: 'Infrastructure Operations Dashboard',
          subtitle: 'High-level telemetry, service health topology and active risk monitoring'
        };
      case 'monitoring':
        return {
          title: 'Infrastructure Telemetry Monitoring',
          subtitle: 'Granular time-series metrics, system utilization curves and microservice endpoints'
        };
      case 'ai-analysis':
        return {
          title: 'Explainable AI & Root Cause Analysis',
          subtitle: 'Multi-model inference, probability calibration, and 4-question investigative insights'
        };
      case 'simulation':
        return {
          title: 'Live Infrastructure Failure Simulation',
          subtitle: 'Interactive test scenarios demonstrating real-time ML anomaly detection & RCA'
        };
      case 'data-reports':
        return {
          title: 'Telemetry Data Ingestion & Audit Reports',
          subtitle: 'Batch CSV dataset analysis, model validation and downloadable diagnostic audits'
        };
      default:
        return { title: 'AIOps Sentinel', subtitle: 'Infrastructure Intelligence' };
    }
  };

  const { title, subtitle } = getSectionTitle();

  return (
    <div className="app-layout">
      {/* Fixed Left Navigation */}
      <Sidebar 
        activeSection={activeSection} 
        onSelectSection={setActiveSection} 
      />

      {/* Main Content Area */}
      <div className="main-wrapper">
        <Header 
          title={title}
          subtitle={subtitle}
          overallHealth={snapshot?.overall_health || 'HEALTHY'}
          riskScore={snapshot?.risk_score || 0}
          onRefresh={fetchGlobalData}
          isRefreshing={isRefreshing}
          onOpenModelModal={() => setIsModelModalOpen(true)}
        />

        <main className="content-container">
          {error && (
            <div style={{
              backgroundColor: 'var(--danger-bg)',
              color: 'var(--danger)',
              border: '1px solid var(--danger-border)',
              padding: '12px 18px',
              borderRadius: 'var(--radius-md)',
              marginBottom: 20,
              fontSize: '0.85rem'
            }}>
              {error}
            </div>
          )}

          {activeSection === 'dashboard' && (
            <DashboardSection 
              snapshot={snapshot} 
              incidents={incidents} 
              onNavigate={setActiveSection}
            />
          )}

          {activeSection === 'monitoring' && (
            <MonitoringSection 
              snapshot={snapshot} 
              onRefresh={fetchGlobalData}
              isRefreshing={isRefreshing}
            />
          )}

          {activeSection === 'ai-analysis' && (
            <AIAnalysisSection 
              currentTelemetry={snapshot?.current} 
              onOpenBenchmarks={() => setIsModelModalOpen(true)}
            />
          )}

          {activeSection === 'simulation' && (
            <SimulationSection 
              onSimulationUpdate={fetchGlobalData}
            />
          )}

          {activeSection === 'data-reports' && (
            <DataReportsSection />
          )}
        </main>
      </div>

      {/* ML Evaluation & Benchmarking Modal */}
      <ModelComparisonModal 
        isOpen={isModelModalOpen} 
        onClose={() => setIsModelModalOpen(false)} 
      />
    </div>
  );
}
