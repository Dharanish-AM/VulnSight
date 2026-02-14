import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.router import router as api_router
from app.core.logger import setup_logging

# Initialize logging
logger = setup_logging()

app = FastAPI(title="VulnSight API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    formatted_process_time = "{0:.2f}ms".format(process_time)
    logger.info(
        f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {formatted_process_time}"
    )
    
    return response

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "VulnSight API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
