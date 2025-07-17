from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database import Base

class Video(Base):
    __tablename__ = "videos"

    # Primary fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500))
    url = Column(String(2048), nullable=False)
    duration = Column(Integer)
    status = Column(String(20), nullable=False, default="pending")
    processing_stage = Column(String(100))  # "downloading", "transcribing", "generating_insights"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    
    # Content
    transcript = Column(Text)
    insights = Column(JSON)
    error = Column(Text)
    
    # Rating system (v1.1.0)
    rating = Column(Integer)  # 1-5 stars
    
    # Basic metadata (v1.2.0)
    uploader = Column(String(255))
    channel = Column(String(255))
    channel_id = Column(String(255))
    uploader_id = Column(String(255))
    view_count = Column(Integer)
    like_count = Column(Integer)
    comment_count = Column(Integer)
    subscriber_count = Column(Integer)
    upload_date = Column(String(50))
    timestamp = Column(Integer)
    release_timestamp = Column(Integer)
    description = Column(Text)
    tags = Column(JSON)  # List of strings
    categories = Column(JSON)  # List of strings
    video_id = Column(String(255))
    webpage_url = Column(String(2048))
    original_url = Column(String(2048))
    extractor = Column(String(100))
    extractor_key = Column(String(100))
    
    # Technical metadata
    resolution = Column(String(50))
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Integer)
    vcodec = Column(String(100))
    acodec = Column(String(100))
    filesize = Column(Integer)
    filesize_approx = Column(Integer)
    language = Column(String(10))
    subtitles = Column(JSON)  # List of subtitle info
    automatic_captions = Column(JSON)  # List of caption info
    age_limit = Column(Integer)
    availability = Column(String(50))
    live_status = Column(String(50))
    was_live = Column(Boolean)
    playable_in_embed = Column(Boolean)
    
    # Additional metadata
    thumbnail = Column(String(2048))
    thumbnails = Column(JSON)  # List of thumbnail objects
    playlist = Column(String(255))
    playlist_id = Column(String(255))
    playlist_title = Column(String(500))
    playlist_index = Column(Integer)
    playlist_count = Column(Integer)
    average_rating = Column(Float)
    abr = Column(Float)  # Audio bitrate
    vbr = Column(Float)  # Video bitrate
    tbr = Column(Float)  # Total bitrate
    channel_follower_count = Column(Integer)
    chapters = Column(JSON)  # List of chapter objects

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        def safe_isoformat(dt):
            """Safely convert datetime to ISO format"""
            if dt is None:
                return None
            try:
                return dt.isoformat()
            except (AttributeError, ValueError):
                return None
        
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "duration": self.duration,
            "status": self.status,
            "processing_stage": self.processing_stage,
            "created_at": safe_isoformat(self.created_at),
            "updated_at": safe_isoformat(self.updated_at),
            "transcript": self.transcript,
            "insights": self.insights,
            "error": self.error,
            "rating": self.rating,
            
            # Extended metadata
            "uploader": self.uploader,
            "channel": self.channel,
            "channel_id": self.channel_id,
            "uploader_id": self.uploader_id,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "subscriber_count": self.subscriber_count,
            "upload_date": self.upload_date,
            "timestamp": self.timestamp,
            "release_timestamp": self.release_timestamp,
            "description": self.description,
            "tags": self.tags,
            "categories": self.categories,
            "video_id": self.video_id,
            "webpage_url": self.webpage_url,
            "original_url": self.original_url,
            "extractor": self.extractor,
            "extractor_key": self.extractor_key,
            "resolution": self.resolution,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "vcodec": self.vcodec,
            "acodec": self.acodec,
            "filesize": self.filesize,
            "filesize_approx": self.filesize_approx,
            "language": self.language,
            "subtitles": self.subtitles,
            "automatic_captions": self.automatic_captions,
            "age_limit": self.age_limit,
            "availability": self.availability,
            "live_status": self.live_status,
            "was_live": self.was_live,
            "playable_in_embed": self.playable_in_embed,
            "thumbnail": self.thumbnail,
            "thumbnails": self.thumbnails,
            "playlist": self.playlist,
            "playlist_id": self.playlist_id,
            "playlist_title": self.playlist_title,
            "playlist_index": self.playlist_index,
            "playlist_count": self.playlist_count,
            "average_rating": self.average_rating,
            "abr": self.abr,
            "vbr": self.vbr,
            "tbr": self.tbr,
            "channel_follower_count": self.channel_follower_count,
            "chapters": self.chapters,
        }