import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, WebSocket, WebSocketDisconnect
from typing import Dict
import logging
from api.schemas.job import JobCreate, JobResponse, JobStage, JobEvent
from api.websockets.manager import manager
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# Very simple in-memory store for MVP. In reality, use Redis or Postgres.
JOBS: Dict[str, dict] = {}

API_TOKEN = os.getenv("API_TOKEN", "super_secret_token_123")

def verify_token(x_token: str = Header(None)):
    if x_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API Token")
    return x_token

@router.post("/", response_model=JobResponse)
async def create_job(job_req: JobCreate, token: str = Depends(verify_token)):
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc)
    
    job_data = {
        "id": job_id,
        "user_id": "user_default",
        "source_url": str(job_req.source_url),
        "status": JobStage.QUEUED,
        "current_stage": JobStage.QUEUED,
        "progress_percent": 0.0,
        "created_at": now,
        "updated_at": now,
        "preset": job_req.preset
    }
    JOBS[job_id] = job_data
    
    # Ideally, trigger Celery task here:
    # from worker.tasks.job_task import process_job
    # process_job.delay(job_id, str(job_req.source_url), job_req.preset.value)
    
    logger.info(f"Created new job {job_id}")
    return JobResponse(**job_data)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, token: str = Depends(verify_token)):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**JOBS[job_id])

@router.delete("/{job_id}/file")
async def delete_job_file(job_id: str, token: str = Depends(verify_token)):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    # MVP logic to "delete" the file
    job = JOBS[job_id]
    output_url = job.get("output_url")
    if output_url:
        filename = output_url.split("/")[-1]
        filepath = os.path.join(os.getcwd(), "storage", filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            job["output_url"] = None
            logger.info(f"Deleted file {filepath} for job {job_id}")
            return {"status": "success", "message": "File deleted"}
    return {"status": "error", "message": "File not found"}

@router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    try:
        while True:
            # We don't expect client to send messages, just keep alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
