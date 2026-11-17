import React, { useState } from 'react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import { 
  UploadCloud, 
  Download, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  FileSpreadsheet, 
  BarChart2, 
  RefreshCw 
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip 
} from 'recharts';

export default function DataReportsSection() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      const res = await api.uploadCSV(file);
      setAnalysisResult(res);
    } catch (err) {
      setError(err.message || 'CSV analysis failed');
    } finally {
      setUploading(false);
    }
  };

  const riskData = analysisResult ? [
    { name: 'Low', count: analysisResult.risk_breakdown?.Low || 0, fill: '#16a34a' },
    { name: 'Moderate', count: analysisResult.risk_breakdown?.Moderate || 0, fill: '#d97706' },
    { name: 'High', count: analysisResult.risk_breakdown?.High || 0, fill: '#ea580c' },
    { name: 'Critical', count: analysisResult.risk_breakdown?.Critical || 0, fill: '#dc2626' },
  ] : [];

  return (
    <div>
      {/* Upload & Sample Download Actions Header */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div>
            <div className="card-title">Infrastructure Telemetry Batch Ingestion & Analysis</div>
            <div className="card-subtitle">Upload multi-metric CSV datasets for offline batch Anomaly Detection & Failure Scoring</div>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <a 
              href={api.getSampleCsvUrl()} 
              download="aiops_sample_telemetry.csv" 
              className="btn btn-secondary btn-sm"
              title="Download realistic test CSV with 120 telemetry rows"
            >
              <Download size={14} />
              <span>Download Sample CSV</span>
            </a>

            <a 
              href={api.getExportReportUrl()} 
              download="aiops_infrastructure_report.txt" 
              className="btn btn-primary btn-sm"
              title="Export current system diagnostic audit summary"
            >
              <FileText size={14} />
              <span>Export Audit Report</span>
            </a>
          </div>
        </div>

        {/* Drag and Drop / File Input Box */}
        <div style={{
          border: '2px dashed var(--border-strong)',
          borderRadius: 'var(--radius-lg)',
          padding: '32px 24px',
          textAlign: 'center',
          backgroundColor: 'var(--bg-subtle)',
          cursor: 'pointer'
        }}>
          <input 
            type="file" 
            accept=".csv" 
            id="csv-file-input" 
            style={{ display: 'none' }} 
            onChange={handleFileChange}
          />
          <label htmlFor="csv-file-input" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <UploadCloud size={40} color="var(--primary)" style={{ marginBottom: 12 }} />
            <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-main)' }}>
              {file ? file.name : 'Click to browse or drop infrastructure telemetry CSV'}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
              Required headers: <code style={{ fontSize: '0.75rem' }}>cpu_utilization, memory_utilization, disk_utilization, network_latency, error_rate</code>
            </div>
          </label>
        </div>

        {file && (
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 16 }}>
            <button 
              className="btn btn-primary btn-sm" 
              onClick={handleUpload} 
              disabled={uploading}
            >
              <RefreshCw size={14} className={uploading ? 'spin-anim' : ''} />
              <span>{uploading ? 'Validating & Running ML Pipeline...' : 'Process Telemetry CSV'}</span>
            </button>
          </div>
        )}
      </div>

      {error && (
        <div style={{ backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', padding: 14, borderRadius: 8, marginBottom: 20 }}>
          {error}
        </div>
      )}

      {/* Batch Analysis Summary Cards */}
      {analysisResult && (
        <>
          <div className="grid-4" style={{ marginBottom: 24 }}>
            <div className="stat-card">
              <div className="stat-label">Total Records Evaluated</div>
              <div className="stat-value font-mono">{analysisResult.total_records}</div>
              <div className="stat-desc">Batch ingestion successful</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Anomalies Detected</div>
              <div className="stat-value font-mono" style={{ color: 'var(--warning)' }}>
                {analysisResult.anomalies_detected}
              </div>
              <div className="stat-desc">Isolation Forest flagging</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Predicted Failures</div>
              <div className="stat-value font-mono" style={{ color: 'var(--danger)' }}>
                {analysisResult.failures_predicted}
              </div>
              <div className="stat-desc">Random Forest failure cutoff (&ge;50%)</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Average CPU Utilization</div>
              <div className="stat-value font-mono">
                {analysisResult.average_metrics?.cpu_utilization}%
              </div>
              <div className="stat-desc">Avg Latency: {analysisResult.average_metrics?.network_latency} ms</div>
            </div>
          </div>

          {/* Risk Level Distribution Chart */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
              <div>
                <div className="card-title">Risk Level Distribution Breakdown</div>
                <div className="card-subtitle">Classification frequency across all ingested telemetry records</div>
              </div>
            </div>

            <div style={{ height: 220, width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={riskData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#fff', borderColor: '#e2e8f0', borderRadius: 6, fontSize: 12 }} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Row-by-Row ML Diagnostic Findings Table */}
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">Record-Level Diagnostic Findings</div>
                <div className="card-subtitle">Showing inspected records with anomaly flags and failure probabilities</div>
              </div>
              <span className="code-pill">Sample Records</span>
            </div>

            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Timestamp</th>
                    <th>CPU</th>
                    <th>Memory</th>
                    <th>Latency</th>
                    <th>Error Rate</th>
                    <th>Anomaly</th>
                    <th>Failure Probability</th>
                    <th>Risk Level</th>
                    <th>Primary Factor</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResult.sample_results?.map((row) => (
                    <tr key={row.row_index}>
                      <td className="code-pill">{row.row_index}</td>
                      <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{row.timestamp}</td>
                      <td className="font-mono">{row.cpu_utilization}%</td>
                      <td className="font-mono">{row.memory_utilization}%</td>
                      <td className="font-mono">{row.network_latency} ms</td>
                      <td className="font-mono">{row.error_rate}%</td>
                      <td>
                        <span style={{ 
                          fontWeight: 600, 
                          fontSize: '0.78rem',
                          color: row.anomaly_detected ? 'var(--warning)' : 'var(--success)' 
                        }}>
                          {row.anomaly_detected ? 'YES' : 'NO'}
                        </span>
                      </td>
                      <td className="font-mono" style={{ 
                        fontWeight: 600,
                        color: row.failure_probability > 0.5 ? 'var(--danger)' : 'var(--text-main)' 
                      }}>
                        {(row.failure_probability * 100).toFixed(1)}%
                      </td>
                      <td><StatusBadge status={row.risk_level} /></td>
                      <td style={{ fontSize: '0.8rem', fontWeight: 500 }}>{row.primary_factor}</td>
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
