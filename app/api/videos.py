from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime, timezone

from ..database import get_db
from ..models import Video, Job
from ..schemas import VideoResponse, VideoCreateRequest, VideoRatingRequest

router = APIRouter()

@router.get("/", response_model=List[VideoResponse])
async def get_videos(db: Session = Depends(get_db)):
    """Get all videos sorted by creation date"""
    videos = db.query(Video).order_by(desc(Video.created_at)).all()
    return [VideoResponse.model_validate(video.to_dict()) for video in videos]

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """Get specific video by ID"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse.model_validate(video.to_dict())

@router.post("/", response_model=VideoResponse)
async def create_video(request: VideoCreateRequest, db: Session = Depends(get_db)):
    """Create a new video and add to processing queue"""
    # Create video record
    video = Video(
        url=request.url,
        status="pending",
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    # Create job for worker
    job = Job(
        video_id=video.id,
        status="pending",
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(job)
    db.commit()
    
    return VideoResponse.model_validate(video.to_dict())

@router.post("/{video_id}/rating")
async def set_video_rating(
    video_id: str, 
    request: VideoRatingRequest, 
    db: Session = Depends(get_db)
):
    """Set rating for a video"""
    if not (1 <= request.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video.rating = request.rating
    video.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {"success": True, "rating": request.rating}

@router.get("/{video_id}/status")
async def get_video_status(video_id: str, db: Session = Depends(get_db)):
    """Get video status (for compatibility with frontend polling)"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "status": video.status,
        "title": video.title,
        "duration": video.duration,
        "channel": video.channel,
        "view_count": video.view_count,
        "upload_date": video.upload_date,
        "transcript": video.transcript,
        "insights": video.insights,
        "error": video.error
    }

@router.post("/{video_id}/insights")
async def generate_insights(video_id: str, db: Session = Depends(get_db)):
    """Generate insights for a completed video (allows regeneration)"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if video.status != "completed":
        raise HTTPException(status_code=400, detail="Video must be completed first")
    
    if not video.transcript:
        raise HTTPException(status_code=400, detail="No transcript available")
    
    # Check if there's already a pending insights job for this video
    existing_job = db.query(Job).filter(
        Job.video_id == video.id,
        Job.status == "pending"
    ).first()
    
    if existing_job:
        raise HTTPException(
            status_code=409, 
            detail="Insights generation already in progress"
        )
    
    # Create job for insights generation (allows regeneration)
    job = Job(
        video_id=video.id,
        status="pending",
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    message = "Insights regeneration started" if video.insights else "Insights generation started"
    return {
        "message": message, 
        "video_id": video_id,
        "job_id": job.id
    }

@router.post("/{video_id}/insights/regenerate")
async def regenerate_insights(video_id: str, db: Session = Depends(get_db)):
    """Regenerate insights for a video that already has insights"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if video.status != "completed":
        raise HTTPException(status_code=400, detail="Video must be completed first")
    
    if not video.transcript:
        raise HTTPException(status_code=400, detail="No transcript available")
    
    if not video.insights:
        raise HTTPException(
            status_code=400, 
            detail="No existing insights found. Use /insights endpoint for initial generation"
        )
    
    # Check if there's already a pending insights job for this video
    existing_job = db.query(Job).filter(
        Job.video_id == video.id,
        Job.status == "pending"
    ).first()
    
    if existing_job:
        raise HTTPException(
            status_code=409, 
            detail="Insights regeneration already in progress"
        )
    
    # Create job for insights regeneration
    job = Job(
        video_id=video.id,
        status="pending",
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return {
        "message": "Insights regeneration started", 
        "video_id": video_id,
        "job_id": job.id
    }