from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./app.db"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Worker Integration
    worker_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins(self):
        return [origin.strip() for origin in self.allowed_origins.split(",")]

settings = Settings()