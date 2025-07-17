from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from ..database import get_db
from ..models import Video, Job
from ..schemas import JobResponse, WorkerJobRequest, WorkerJobResult, WorkerClaimRequest, WorkerJobProgress
from ..config import settings

router = APIRouter()

def verify_worker_token(x_worker_token: str = Header(None)):
    """Verify worker authentication token"""
    if settings.worker_api_key and x_worker_token != settings.worker_api_key:
        raise HTTPException(status_code=401, detail="Invalid worker token")
    return True

@router.get("/jobs", response_model=List[JobResponse])
async def get_pending_jobs(
    limit: int = 10,
    worker_verified: bool = Depends(verify_worker_token),
    db: Session = Depends(get_db)
):
    """Get pending jobs for worker to process"""
    jobs = db.query(Job).filter(
        Job.status == "pending"
    ).order_by(Job.created_at).limit(limit).all()
    
    return [JobResponse.model_validate(job.to_dict()) for job in jobs]

@router.post("/jobs/{job_id}/claim")
async def claim_job(
    job_id: str,
    request: WorkerClaimRequest,
    worker_verified: bool = Depends(verify_worker_token),
    db: Session = Depends(get_db)
):
    """Claim a job for processing"""
    job = db.query(Job).filter(Job.id == job_id, Job.status == "pending").first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or already claimed")
    
    # Update job status
    job.status = "processing"
    job.worker_id = request.worker_id
    job.started_at = datetime.now(timezone.utc)
    job.updated_at = datetime.now(timezone.utc)
    
    # Update video status
    video = db.query(Video).filter(Video.id == job.video_id).first()
    if video:
        video.status = "processing"
        video.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {
        "success": True,
        "job_id": job_id,
        "video_url": video.url if video else None
    }

@router.post("/jobs/{job_id}/result")
async def submit_job_result(
    job_id: str,
    result: WorkerJobResult,
    worker_verified: bool = Depends(verify_worker_token),
    db: Session = Depends(get_db)
):
    """Submit job result from worker"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    video = db.query(Video).filter(Video.id == job.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Update job
    job.status = result.status
    job.completed_at = datetime.now(timezone.utc)
    job.updated_at = datetime.now(timezone.utc)
    
    if result.status == "failed":
        job.error_message = result.error
    
    # Update video
    video.status = result.status
    video.updated_at = datetime.now(timezone.utc)
    
    if result.status == "completed":
        video.transcript = result.transcript
        video.insights = result.insights
        
        # Update metadata if provided
        if result.metadata:
            for key, value in result.metadata.items():
                if hasattr(video, key):
                    setattr(video, key, value)
    
    elif result.status == "failed":
        video.error = result.error
    
    db.commit()
    
    return {"success": True, "message": f"Job {job_id} updated successfully"}

@router.post("/jobs/{job_id}/progress")
async def update_job_progress(
    job_id: str,
    progress: dict,
    worker_verified: bool = Depends(verify_worker_token),
    db: Session = Depends(get_db)
):
    """Update job progress from worker"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.progress = progress
    job.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {"success": True}

@router.post("/jobs/{job_id}/stage")
async def update_job_stage(
    job_id: str,
    progress: WorkerJobProgress,
    worker_verified: bool = Depends(verify_worker_token),
    db: Session = Depends(get_db)
):
    """Update processing stage for a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    video = db.query(Video).filter(Video.id == job.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Update video processing stage
    video.processing_stage = progress.processing_stage
    video.updated_at = datetime.now(timezone.utc)
    
    # Also update job progress
    job.progress = {"stage": progress.processing_stage}
    job.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {"success": True, "stage": progress.processing_stage}