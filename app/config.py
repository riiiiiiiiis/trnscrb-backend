from pydantic_settings import BaseSettings
from typing import Optional, List
import logging
from urllib.parse import urlparse

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
    def cors_origins(self) -> List[str]:
        """Parse and validate CORS origins from environment variable"""
        logger = logging.getLogger(__name__)
        
        # Split and clean origins
        raw_origins = [origin.strip() for origin in self.allowed_origins.split(",")]
        validated_origins = []
        
        for origin in raw_origins:
            # Skip empty origins
            if not origin:
                continue
                
            # Validate URL format
            try:
                parsed = urlparse(origin)
                if not parsed.scheme or not parsed.netloc:
                    logger.warning(f"Skipping invalid origin (missing scheme or netloc): {origin}")
                    continue
                    
                if parsed.scheme not in ['http', 'https']:
                    logger.warning(f"Skipping invalid origin (unsupported scheme): {origin}")
                    continue
                    
                # Remove trailing slash for consistency
                clean_origin = f"{parsed.scheme}://{parsed.netloc}"
                if parsed.port:
                    clean_origin = f"{parsed.scheme}://{parsed.netloc}"
                    
                validated_origins.append(clean_origin)
                
            except Exception as e:
                logger.warning(f"Skipping malformed origin: {origin} - {str(e)}")
                continue
        
        # Fallback to defaults if no valid origins found
        if not validated_origins:
            logger.warning("No valid origins found, falling back to development defaults")
            validated_origins = ["http://localhost:3000", "http://localhost:5173"]
            
        return validated_origins

settings = Settings()