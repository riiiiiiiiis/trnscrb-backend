from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .api import videos, worker
from .config import settings

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield

# Create FastAPI app
app = FastAPI(
    title="Transcribe.Cafe Backend",
    description="Backend API for YouTube transcription service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(worker.router, prefix="/api/worker", tags=["worker"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "transcribe-backend",
        "version": "1.0.0"
    }

@app.get("/api/info")
async def api_info():
    """API information and architecture type"""
    return {
        "service": "transcribe-backend",
        "architecture": "separated",
        "version": "1.0.0",
        "database": "SQLAlchemy + SQLite/PostgreSQL",
        "features": [
            "worker-api-integration",
            "alembic-migrations", 
            "railway-ready",
            "production-architecture"
        ],
        "endpoints": {
            "videos": "/api/videos",
            "worker": "/api/worker",
            "docs": "/docs"
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Transcribe.Cafe Backend API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )