from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import asyncio
import time
from scanner import VulnScanner
from parser import ScanParser
from chat import AIAnalyzer
from logger import get_logger

logger = get_logger("API")

app = FastAPI(title="VulnSight API")
logger.info("VulnSight API is starting up...")

# Enable CORS for frontend
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming {request.method} request to {request.url.path}")
    response = await call_next(request)
    logger.info(f"Completed {request.method} request to {request.url.path} with status {response.status_code}")
    return response

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = ScanParser()
analyzer = AIAnalyzer()

DATA_FILE = "data/latest_scan.json"

class ScanRequest(BaseModel):
    target: str

class ChatRequest(BaseModel):
    question: str
    scan_id: str = "latest"

@app.post("/scan")
async def run_scan(request: ScanRequest):
    try:
        logger.info(f"Processing ultra-fast scan for target: {request.target}")
        logger.warning(f"Two-stage scanning active. Phase 1: Rapid discovery. Phase 2: Targeted scripts. Est. time: 10-60 seconds.")
        start_time = time.time()
        
        # Instantiate scanner per-request for thread-safety
        request_scanner = VulnScanner()
        
        # Start a heartbeat logger to reassure the user during long scans
        async def heartbeat():
            while True:
                await asyncio.sleep(30)
                elapsed = int(time.time() - start_time)
                logger.info(f"Scan for {request.target} still in progress... ({elapsed}s elapsed)")

        heartbeat_task = asyncio.create_task(heartbeat())
        
        try:
            raw_data = await asyncio.to_thread(request_scanner.scan, request.target)
        finally:
            heartbeat_task.cancel()
            try: await heartbeat_task
            except asyncio.CancelledError: pass
        
        if not raw_data or "error" in raw_data:
            error_detail = raw_data.get("error", "Unknown scan error") if raw_data else "No data returned from scanner"
            raise HTTPException(status_code=500, detail=str(error_detail))
        
        # If no host found or no ports open, the raw_data might be basic but valid
        if not raw_data.get("tcp"):
             logger.info(f"No open tcp ports found on {request.target}.")
        
        parsed_results = parser.parse(raw_data)
        
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(parsed_results, f, indent=4)
        
        duration = time.time() - start_time
        logger.info(f"Ultra-fast scan workflow completed for {request.target} in {duration:.2f}s")
        return parsed_results
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during scan for {request.target}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
async def get_results():
    if not os.path.exists(DATA_FILE):
        return {"results": [], "target": "None"}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    logger.info(f"Received chat request: {request.question}")
    if not os.path.exists(DATA_FILE):
        logger.warning("Chat requested but no scan results available")
        raise HTTPException(status_code=400, detail="No scan results available.")
    
    with open(DATA_FILE, "r") as f:
        scan_results = json.load(f)
        
    response = await analyzer.analyze_vulnerabilities(scan_results, request.question)
    logger.info("AI analysis completed")
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
