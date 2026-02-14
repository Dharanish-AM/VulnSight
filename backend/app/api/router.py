from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
import os
from app.scanners.nmap_adapter import NmapAdapter
from app.scanners.nuclei_adapter import NucleiAdapter
from app.scanners.nikto_adapter import NiktoAdapter
from app.services.normalization import normalize_results
from app.services.enrichment import enrich_vulnerability
from app.attack_graph.attack_chain import AttackGraphEngine
from app.rag.rag_service import RAGService

router = APIRouter()

# Global state for MVP (would be in Redis/DB in prod)
scans = {}

class ScanRequest(BaseModel):
    target: str

class ChatRequest(BaseModel):
    query: str
    scan_id: Optional[str] = None

nmap = NmapAdapter()
nuclei = NucleiAdapter()
nikto = NiktoAdapter()
attack_engine = AttackGraphEngine()
rag = RAGService()

from concurrent.futures import ThreadPoolExecutor

def run_pipeline(scan_id: str, target: str):
    scans[scan_id]["status"] = "running"
    
    # Execution in parallel
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_nmap = executor.submit(nmap.run_scan, target)
        future_nuclei = executor.submit(nuclei.run_scan, target)
        future_nikto = executor.submit(nikto.run_scan, target)
        
        results.extend(future_nmap.result())
        results.extend(future_nuclei.result())
        results.extend(future_nikto.result())
    
    # Normalization
    normalized = normalize_results(results)
    
    # Enrichment
    for v in normalized:
        extra = enrich_vulnerability(v["cve_id"])
        if extra:
            v.update(extra)
            
    # Attack Path
    attack_engine.generate_graph(normalized)
    chains = attack_engine.get_ranked_chains()
    
    # Index for RAG
    rag.index_report(scan_id, normalized)
    
    # Storage
    report = {
        "id": scan_id,
        "target": target,
        "vulnerabilities": normalized,
        "attack_paths": chains,
        "status": "completed"
    }
    
    scans[scan_id] = report
    
    # Save to file system for persistence in MVP
    os.makedirs("app/data/reports", exist_ok=True)
    with open(f"app/data/reports/{scan_id}.json", "w") as f:
        json.dump(report, f)

@router.post("/scan/start")
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    scan_id = str(uuid.uuid4())
    scans[scan_id] = {"status": "queued", "target": request.target}
    background_tasks.add_task(run_pipeline, scan_id, request.target)
    return {"scan_id": scan_id, "status": "queued"}

@router.get("/scan/status/{id}")
async def get_status(id: str):
    if id not in scans:
        # Try loading from file
        path = f"app/data/reports/{id}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                scans[id] = json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Scan not found")
    
    return {"status": scans[id].get("status", "unknown")}

@router.get("/scan/report/{id}")
async def get_report(id: str):
    if id not in scans:
        path = f"app/data/reports/{id}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                scans[id] = json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Scan not found")
            
    if scans[id].get("status") != "completed":
        raise HTTPException(status_code=400, detail="Scan not yet completed")
        
    return scans[id]

@router.post("/chat/query")
async def chat_query(request: ChatRequest):
    if request.scan_id and request.scan_id not in scans:
        # Attempt to recover from file for RAG context
        path = f"app/data/reports/{request.scan_id}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                report = json.load(f)
                scans[request.scan_id] = report
                # Re-index for RAG if it was a completed scan
                if report.get("status") == "completed":
                    rag.index_report(request.scan_id, report.get("vulnerabilities", []))
                    
    response = rag.query(request.query, request.scan_id)
    return response
