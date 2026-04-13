from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import jobs
import logging
from dotenv import load_dotenv
import os
from fastapi.staticfiles import StaticFiles

load_dotenv()

logging.basicConfig(level=logging.INFO, filename='logs/api.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI(title="Remote Media Relay API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

# Ensure storage directory exists and mount it for downloads
os.makedirs("storage", exist_ok=True)
app.mount("/files", StaticFiles(directory="storage"), name="files")

@app.get("/health")
def health_check():
    return {"status": "ok"}
