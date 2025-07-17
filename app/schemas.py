from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request schemas
class VideoCreateRequest(BaseModel):
    url: str

class VideoRatingRequest(BaseModel):
    rating: int

# Response schemas
class VideoResponse(BaseModel):
    id: str
    title: Optional[str] = None
    url: str
    duration: Optional[int] = None
    status: str
    processing_stage: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    transcript: Optional[str] = None
    insights: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    rating: Optional[int] = None
    
    # Extended metadata fields
    uploader: Optional[str] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    uploader_id: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    subscriber_count: Optional[int] = None
    upload_date: Optional[str] = None
    timestamp: Optional[int] = None
    release_timestamp: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    video_id: Optional[str] = None
    webpage_url: Optional[str] = None
    original_url: Optional[str] = None
    extractor: Optional[str] = None
    extractor_key: Optional[str] = None
    resolution: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    language: Optional[str] = None
    subtitles: Optional[Any] = None  # Can be List[Dict] or Any
    automatic_captions: Optional[Any] = None  # Can be List[Dict] or Any
    age_limit: Optional[int] = None
    availability: Optional[str] = None
    live_status: Optional[str] = None
    was_live: Optional[bool] = None
    playable_in_embed: Optional[bool] = None
    thumbnail: Optional[str] = None
    thumbnails: Optional[Any] = None  # Can be List[Dict] or Any
    playlist: Optional[str] = None
    playlist_id: Optional[str] = None
    playlist_title: Optional[str] = None
    playlist_index: Optional[int] = None
    playlist_count: Optional[int] = None
    average_rating: Optional[float] = None
    abr: Optional[float] = None  # Can be float
    vbr: Optional[float] = None  # Can be float
    tbr: Optional[float] = None  # Can be float
    channel_follower_count: Optional[int] = None
    chapters: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: str
    video_id: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    worker_id: Optional[str] = None
    error_message: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# Worker integration schemas
class WorkerJobRequest(BaseModel):
    video_id: str
    url: str

class WorkerClaimRequest(BaseModel):
    worker_id: str

class WorkerJobResult(BaseModel):
    video_id: str
    status: str  # completed, failed
    processing_stage: Optional[str] = None  # downloading, transcribing, generating_insights
    transcript: Optional[str] = None
    insights: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None  # Extended video metadata

class WorkerJobProgress(BaseModel):
    video_id: str
    processing_stage: str  # downloading, transcribing, generating_insights