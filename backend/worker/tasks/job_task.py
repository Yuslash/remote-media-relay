import os
import time
import uuid
import logging
from celery import shared_task
from worker.utils.ffmpeg import process_video

logger = logging.getLogger(__name__)

# Basic mock of sending updates via redis which WebSocket manager consumes
# In a real app we'd broadcast this. We can use Redis pubsub.
# Here we'll just log it since the FastAPI processes and Celery processes are separate
# and we're just aiming for MVP correctness.

@shared_task(name="worker.tasks.job_task.process_job")
def process_job(job_id: str, source_url: str, preset: str):
    logger.info(f"Starting job {job_id} with url {source_url} and preset {preset}")
    
    # 1. QUEUED -> DOWNLOADING
    logger.info(f"[{job_id}] Downloading...")
    time.sleep(2) # Mock download time
    
    # 2. DOWNLOADING -> ANALYZING
    logger.info(f"[{job_id}] Analyzing...")
    time.sleep(1) # Mock analyze time
    
    # 3. ANALYZING -> CONVERTING
    logger.info(f"[{job_id}] Converting...")
    input_file = "mock_input.mp4" # Just a placeholder
    output_filename = f"{job_id}.mp4"
    output_filepath = os.path.join(os.getcwd(), 'storage', output_filename)
    
    try:
        # In MVP, we mock the real ffmpeg call to prevent crash if not correctly installed
        # process_video(input_file, output_filepath, preset, job_id)
        # Mocking progress
        for i in range(40, 86, 10):
            logger.info(f"[{job_id}] Conversion progress: {i}%")
            time.sleep(1)
        
        # Keep an empty file to simulate result
        with open(output_filepath, 'w') as f:
            f.write("Mock video data")
            
    except Exception as e:
        logger.error(f"[{job_id}] Conversion failed: {e}")
        return {"status": "failed", "error": str(e)}

    # 4. UPLOADING -> COMPLETED
    logger.info(f"[{job_id}] Completed.")
    
    return {"status": "completed", "output_url": f"/files/{output_filename}"}
