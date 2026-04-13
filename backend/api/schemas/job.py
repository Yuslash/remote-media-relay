from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict
from enum import Enum
from datetime import datetime

class JobStage(str, Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    CONVERTING = "converting"
    OPTIMIZING = "optimizing"
    VERIFYING = "verifying"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PresetEnum(str, Enum):
    DISCORD_DEFAULT = "discord_default"
    DISCORD_SMALL = "discord_small"
    HIGH_QUALITY = "discord_high_quality"

class JobCreate(BaseModel):
    source_url: HttpUrl
    preset: PresetEnum = PresetEnum.DISCORD_DEFAULT

class JobResponse(BaseModel):
    id: str
    user_id: str
    source_url: str
    status: JobStage
    current_stage: JobStage
    progress_percent: float
    input_filename: Optional[str] = None
    output_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class JobEvent(BaseModel):
    jobId: str
    stage: JobStage
    percent: float
    message: str
    timestamp: str
    meta: Dict = {}
