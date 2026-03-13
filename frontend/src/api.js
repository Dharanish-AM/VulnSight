const API_BASE = "http://localhost:8000";

export const api = {
  async startScan(target) {
    const response = await fetch(`${API_BASE}/scan/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target }),
    });
    return response.json();
  },

  async getStatus(id) {
    const response = await fetch(`${API_BASE}/scan/status/${id}`);
    return response.json();
  },

  async getReport(id) {
    const response = await fetch(`${API_BASE}/scan/report/${id}`);
    return response.json();
  },

  async askAI(query, scanId = null) {
    const response = await fetch(`${API_BASE}/chat/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, scan_id: scanId }),
    });
    return response.json();
  },

  async listScans() {
    const response = await fetch(`${API_BASE}/scans`);
    return response.json();
  },

  async deleteScan(id) {
    const response = await fetch(`${API_BASE}/scan/${id}`, {
      method: "DELETE",
    });
    return response.json();
  },

  async exportReport(id, format) {
    if (format === 'csv') {
      window.open(`${API_BASE}/scan/export/${id}/csv`, '_blank');
      return;
    }
    const response = await fetch(`${API_BASE}/scan/export/${id}/${format}`);
    return response.json();
  },
};

