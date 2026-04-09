<p align="center">
  <img src="/Users/dharanisham/.gemini/antigravity/brain/eb2d2834-4150-4035-b0ac-fb4d61a383d7/vulnsight_logo_1775747123961.png" width="350" alt="VulnSight Logo">
</p>

# 🦅 VulnSight: Intelligent Cybersecurity Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![VulnSight](https://img.shields.io/badge/Neural--Core-RAG--Powered-blue?style=for-the-badge)](https://github.com/Dharanish-AM/VulnSight)

**VulnSight** is a production-grade, modular vulnerability management system. It orchestrates industry-standard scanning tools, normalizes disparate security data, predicts sophisticated attack paths, and provides a RAG-powered AI interface for real-time security intelligence.

---

## 🚀 Core Capabilities

- **Unified Scanning Pipeline**: Native integration with `Nmap`, `Nuclei`, `Nikto`, `SQLMap`, and `FFUF` via pluggable adapters.
- **Intelligent Normalization**: Deduplicates findings across tools and standardizes them into a high-fidelity schema.
- **Threat Enrichment**: Injects live CVE data, CVSS scoring, and detailed remediation guidance.
- **Attack Graph Engine**: Uses NetworkX to model infrastructure dependencies and predict potential lateral movement paths.
- **"Neural Core" RAG Interface**: A scan-aware AI system that uses **ChromaDB** to provide context-specific security advice.
- **Cyber-Tactical Dashboard**: A modern React-based interface with real-time telemetry, live SSE log streaming, and advanced data visualization.

---

## 🏗 System Architecture

```mermaid
graph TD
    subgraph Frontend
        UI[React Dashboard]
        SSE[Live Log Streamer]
    end

    subgraph API_Layer
        API[FastAPI Router]
        BT[Background Task Engine]
    end

    subgraph Scanning_Orchestrator
        AD1[Nmap Adapter]
        AD2[Nuclei Adapter]
        AD3[Nikto Adapter]
        AD4[FFUF Adapter]
        AD5[SQLMap Adapter]
    end

    subgraph Intelligence_Engines
        NORM[Normalization Service]
        ENR[CVE Enrichment]
        AGE[Attack Graph Engine]
    end

    subgraph Vector_Intelligence
        VAULT[ChromaDB Vector Store]
        RAG[RAG Query Service]
        LLM[Neural Core AI]
    end

    UI <--> API
    API --> SSE
    API --> BT
    BT --> AD1 & AD2 & AD3 & AD4 & AD5
    AD1 & AD2 & AD3 & AD4 & AD5 --> NORM
    NORM --> ENR
    ENR --> AGE
    AGE --> VAULT
    VAULT <--> RAG
    RAG <--> LLM
```

---

## 📁 Project Structure

```text
VulnSight/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI Endpoint Routers
│   │   ├── scanners/        # Tool-specific adapter logic (Nmap, Nikto, SSE, etc.)
│   │   ├── services/        # Logic for normalization and enrichment
│   │   ├── attack_graph/    # NetworkX-based path prediction
│   │   ├── rag/             # Vector DB and RAG pipeline
│   │   └── data/            # Local scan state, logs, and reports
│   ├── main.py              # Application Entry Point
│   └── requirements.txt     # Python Dependencies
├── frontend/
│   ├── src/                 # React Application (Vite-powered)
│   │   ├── App.jsx          # Main UI Orchestrator
│   │   └── index.css        # Premium Dark-Mode Styles
│   └── package.json         # Node Dependencies
└── scripts/
    ├── start_backend.sh     # Automation script for Backend
    └── start_frontend.sh    # Automation script for Frontend
```

---

## 🛠 Installation & Setup

### Prerequisites (macOS)

Ensure you have the core scanning tools installed. You can install them using [Homebrew](https://brew.sh/):

```bash
brew install nmap nuclei nikto sqlmap ffuf
```

> [!NOTE]
> If tools are missing, the system will gracefully switch to safe mock-telemetry to allow UI and Intelligence engine testing.

### 1. Backend Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 2. Frontend Environment

```bash
cd frontend
npm install
npm run dev
```

---

## ⚡ Troubleshooting & Compatibility

### 🧠 ChromaDB & Python 3.14+

If you are running **Python 3.14+**, you may encounter a `ConfigError` related to ChromaDB's dependencies. VulnSight includes an **Intelligent Fallback Layer**:

- If `chromadb` fails to initialize, the system automatically enables an **In-Memory Search Service**.
- This ensures the "Neural Core" chatbot remains functional even without a native vector store.

### 📦 Missing Dependencies

If you encounter `ModuleNotFoundError: No module named 'networkx'`, ensure your virtual environment is activated:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🧪 Advanced Testing

We provide a specialized script to test the entire lifecycle (Scan → Normalize → Attack Path → RAG Query):

```bash
cd backend
python test_e2e.py
```

This script will:
1. Trigger a live scan.
2. Poll until results are enriched.
3. Validate attack chain generation.
4. Execute a successful RAG query against the "Neural Core".

---

## 🔒 Security

- **Strict Input Validation**: Sanity checks on all target IP/Domain strings.
- **Process Isolation**: Scanners run in isolated subprocesses with restricted shell execution.
- **No Hardcoded Secrets**: All configurations are modularized and environment-driven.

---

<p align="center">
  Built with ❤️ by the VulnSight Team
</p>
