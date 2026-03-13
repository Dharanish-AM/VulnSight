from fastapi import APIRouter, BackgroundTasks, HTTPException, Response
from fastapi.responses import FileResponse
import csv
import io
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
indexed_scans = set()

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
    indexed_scans.add(scan_id)
    
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
    os.makedirs("data/reports", exist_ok=True)
    with open(f"data/reports/{scan_id}.json", "w") as f:
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
        path = f"data/reports/{id}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                scans[id] = json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Scan not found")
    
    return {"status": scans[id].get("status", "unknown")}

def ensure_indexed(scan_id: str):
    if scan_id in scans and scan_id not in indexed_scans:
        report = scans[scan_id]
        if report.get("status") == "completed":
            rag.index_report(scan_id, report.get("vulnerabilities", []))
            indexed_scans.add(scan_id)

@router.get("/scan/report/{id}")
async def get_report(id: str):
    if id not in scans:
        path = f"data/reports/{id}.json"
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
    if request.scan_id:
        if request.scan_id not in scans:
            # Attempt to recover from file for RAG context
            path = f"data/reports/{request.scan_id}.json"
            if os.path.exists(path):
                with open(path, "r") as f:
                    report = json.load(f)
                    scans[request.scan_id] = report
        
        ensure_indexed(request.scan_id)
                    
    response = rag.query(request.query, request.scan_id)
    return response

@router.get("/scans")
async def list_scans():
    all_scans = []
    reports_dir = "data/reports"
    
    # First, combine in-memory scans
    for sid, data in scans.items():
        all_scans.append({
            "id": sid,
            "target": data.get("target"),
            "status": data.get("status"),
            "vulnerability_count": len(data.get("vulnerabilities", [])),
            "timestamp": os.path.getmtime(f"{reports_dir}/{sid}.json") if os.path.exists(f"{reports_dir}/{sid}.json") else None
        })
    
    # Then look for files not in memory
    if os.path.exists(reports_dir):
        for filename in os.listdir(reports_dir):
            if filename.endswith(".json"):
                sid = filename[:-5]
                if sid not in scans:
                    path = f"{reports_dir}/{filename}"
                    with open(path, "r") as f:
                        try:
                            data = json.load(f)
                            all_scans.append({
                                "id": sid,
                                "target": data.get("target"),
                                "status": data.get("status"),
                                "vulnerability_count": len(data.get("vulnerabilities", [])),
                                "timestamp": os.path.getmtime(path)
                            })
                        except:
                            continue
                            
    # Sort by timestamp decending
    all_scans.sort(key=lambda x: x["timestamp"] or 0, reverse=True)
    return all_scans

@router.delete("/scan/{id}")
async def delete_scan(id: str):
    if id in scans:
        del scans[id]
        
    path = f"data/reports/{id}.json"
    if os.path.exists(path):
        os.remove(path)
        return {"status": "deleted"}
    
    raise HTTPException(status_code=404, detail="Scan not found")

@router.get("/scan/export/{id}/{format}")
async def export_report(id: str, format: str):
    # Load report
    report = None
    if id in scans:
        report = scans[id]
    else:
        path = f"data/reports/{id}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                report = json.load(f)
                
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if format.lower() == "json":
        return report
    
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["CVE ID", "Component", "Severity", "Description", "CVSS", "Source Tool"])
        
        # Data
        for v in report.get("vulnerabilities", []):
            writer.writerow([
                v.get("cve_id", "N/A"),
                v.get("component", "N/A"),
                v.get("severity", "N/A"),
                v.get("description", "N/A"),
                v.get("cvss", "N/A"),
                v.get("source_tool", "N/A")
            ])
            
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=vulnsight_report_{id}.csv"}
        )
        
    raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'csv'.")

