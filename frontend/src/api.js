const API_BASE = "http://localhost:8000";

export const api = {
  async scan(target) {
    const response = await fetch(`${API_BASE}/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target }),
    });
    return response.json();
  },

  async getLatestResults() {
    const response = await fetch(`${API_BASE}/results`);
    return response.json();
  },

  async askAI(question) {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    return response.json();
  },
};
