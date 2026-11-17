// API client for AIOps Sentinel
const API_BASE = import.meta.env.VITE_BACKEND_URL || '';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Accept': 'application/json',
        ...(options.headers || {})
      }
    });

    if (!res.ok) {
      let errorMsg = `Server error ${res.status}`;
      try {
        const errorData = await res.json();
        errorMsg = errorData.detail || errorMsg;
      } catch (e) {
        // fallback
      }
      throw new Error(errorMsg);
    }

    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Telemetry
  getTelemetrySnapshot: () => request('/api/telemetry/snapshot'),
  getTelemetryHistory: () => request('/api/telemetry/history'),
  
  // Machine Learning & Explainable AI
  predict: (data) => request('/api/ml/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }),
  getModelMetrics: () => request('/api/ml/metrics'),
  retrainModels: () => request('/api/ml/retrain', { method: 'POST' }),

  // Live Simulation
  getSimulationScenarios: () => request('/api/simulation/scenarios'),
  getSimulationStatus: () => request('/api/simulation/status'),
  controlSimulation: (action, scenario = 'normal') => request('/api/simulation/control', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, scenario })
  }),
  stepSimulation: () => request('/api/simulation/step', { method: 'POST' }),

  // Incidents
  getIncidents: () => request('/api/incidents'),
  updateIncidentStatus: (id, status, actionTaken = null) => request(`/api/incidents/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, action_taken: actionTaken })
  }),

  // Data & Reports
  uploadCSV: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const url = `${API_BASE}/api/data/upload`;
    const res = await fetch(url, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Upload failed with status ${res.status}`);
    }
    return await res.json();
  },
  getSampleCsvUrl: () => `${API_BASE}/api/data/sample-csv`,
  getExportReportUrl: () => `${API_BASE}/api/data/export-report`
};
