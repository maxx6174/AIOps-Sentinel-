import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { X, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

export default function ModelComparisonModal({ isOpen, onClose }) {
  const [metricsData, setMetricsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getModelMetrics();
      setMetricsData(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch model metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchMetrics();
    }
  }, [isOpen]);

  const handleRetrain = async () => {
    try {
      setRetraining(true);
      await api.retrainModels();
      await fetchMetrics();
    } catch (err) {
      setError(err.message || 'Retraining failed');
    } finally {
      setRetraining(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Machine Learning Model Evaluation & Verification
            </h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Comparative benchmark of trained models on infrastructure telemetry (Leakage-free split).
            </p>
          </div>
          <button 
            onClick={onClose} 
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
          >
            <X size={20} />
          </button>
        </div>

        {error && (
          <div style={{ 
            backgroundColor: 'var(--danger-bg)', 
            color: 'var(--danger)', 
            padding: '10px 14px', 
            borderRadius: 'var(--radius-md)', 
            marginBottom: 16,
            fontSize: '0.85rem'
          }}>
            {error}
          </div>
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
            Loading model benchmarks...
          </div>
        ) : metricsData ? (
          <div>
            {/* Comparative Metrics Table */}
            <h3 style={{ fontSize: '0.92rem', fontWeight: 600, marginBottom: 10, color: 'var(--text-main)' }}>
              Model Performance Comparison
            </h3>
            <div className="table-wrapper" style={{ marginBottom: 24 }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Type</th>
                    <th>Accuracy</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1 Score</th>
                    <th>ROC-AUC</th>
                  </tr>
                </thead>
                <tbody>
                  {metricsData.models.map((m, idx) => (
                    <tr key={idx} style={{ fontWeight: m.model_name.includes('Random Forest') ? 600 : 400 }}>
                      <td>{m.model_name}</td>
                      <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{m.model_type}</td>
                      <td className="font-mono">{(m.accuracy * 100).toFixed(1)}%</td>
                      <td className="font-mono">{(m.precision * 100).toFixed(1)}%</td>
                      <td className="font-mono">{(m.recall * 100).toFixed(1)}%</td>
                      <td className="font-mono" style={{ color: 'var(--primary)', fontWeight: 600 }}>
                        {m.f1_score.toFixed(4)}
                      </td>
                      <td className="font-mono">{m.roc_auc ? m.roc_auc.toFixed(4) : 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Random Forest Feature Importance */}
            {metricsData.models[0]?.feature_importances && (
              <div style={{ marginBottom: 24 }}>
                <h3 style={{ fontSize: '0.92rem', fontWeight: 600, marginBottom: 10, color: 'var(--text-main)' }}>
                  Random Forest Feature Importances (Global Attribution)
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {Object.entries(metricsData.models[0].feature_importances).map(([feat, imp]) => (
                    <div key={feat} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <span style={{ width: 160, fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                        {feat.replace('_', ' ')}:
                      </span>
                      <div style={{ flex: 1, backgroundColor: 'var(--bg-subtle)', height: 8, borderRadius: 4, overflow: 'hidden' }}>
                        <div style={{ 
                          width: `${imp * 100}%`, 
                          backgroundColor: 'var(--primary)', 
                          height: '100%', 
                          borderRadius: 4 
                        }}></div>
                      </div>
                      <span className="font-mono" style={{ width: 60, fontSize: '0.82rem', textAlign: 'right', fontWeight: 600 }}>
                        {(imp * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Dataset Information */}
            <div style={{ 
              backgroundColor: 'var(--bg-subtle)', 
              borderRadius: 'var(--radius-md)', 
              padding: '14px 18px',
              fontSize: '0.82rem',
              color: 'var(--text-muted)',
              marginBottom: 20
            }}>
              <p><strong>Dataset:</strong> {metricsData.dataset_info?.dataset_type}</p>
              <p><strong>Split:</strong> {metricsData.dataset_info?.train_samples} Train / {metricsData.dataset_info?.test_samples} Test (25% Stratified Holdout)</p>
              <p><strong>Baseline Failure Rate:</strong> {(metricsData.dataset_info?.failure_rate * 100).toFixed(1)}%</p>
              <p><strong>Last Evaluated:</strong> {new Date(metricsData.last_trained).toLocaleString()}</p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
              <button 
                className="btn btn-secondary btn-sm" 
                onClick={handleRetrain} 
                disabled={retraining}
              >
                <RefreshCw size={14} className={retraining ? 'spin-anim' : ''} />
                <span>{retraining ? 'Retraining ML Pipeline...' : 'Re-run Training & Evaluation'}</span>
              </button>
              <button className="btn btn-primary btn-sm" onClick={onClose}>
                Done
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
