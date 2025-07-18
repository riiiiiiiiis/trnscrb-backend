import pytest
import os
from unittest.mock import patch
from app.config import Settings


class TestBackwardCompatibility:
    """Test suite to validate backward compatibility with existing development setup"""
    
    def test_default_behavior_without_env_vars(self):
        """Test that default localhost origins work when no environment variables are set"""
        # Clear any existing ALLOWED_ORIGINS environment variable
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            origins = settings.cors_origins
            
            # Should have default development origins
            assert len(origins) == 2
            assert "http://localhost:3000" in origins
            assert "http://localhost:5173" in origins
    
    def test_env_file_configuration_override(self):
        """Test that .env file configuration properly overrides defaults"""
        # Simulate .env file setting ALLOWED_ORIGINS
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'https://production.example.com,http://localhost:8080'}):
            settings = Settings()
            origins = settings.cors_origins
            
            # Should use environment variable values, not defaults
            assert len(origins) == 2
            assert "https://production.example.com" in origins
            assert "http://localhost:8080" in origins
            # Should not include default origins
            assert "http://localhost:3000" not in origins
            assert "http://localhost:5173" not in origins
    
    def test_development_mode_behavior(self):
        """Test that development mode continues to work as expected"""
        # Test with typical development environment
        with patch.dict(os.environ, {'DEBUG': 'True'}):
            settings = Settings()
            
            # Debug mode should be enabled
            assert settings.debug is True
            
            # Default CORS origins should still work
            origins = settings.cors_origins
            assert "http://localhost:3000" in origins
            assert "http://localhost:5173" in origins
    
    def test_existing_env_patterns_preserved(self):
        """Test that existing environment variable patterns continue to work"""
        env_vars = {
            'DATABASE_URL': 'sqlite:///./test.db',
            'API_HOST': '127.0.0.1',
            'API_PORT': '9000',
            'DEBUG': 'False',
            'ALLOWED_ORIGINS': 'http://localhost:3000,http://localhost:5173'
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            
            # All existing settings should work
            assert settings.database_url == 'sqlite:///./test.db'
            assert settings.api_host == '127.0.0.1'
            assert settings.api_port == 9000
            assert settings.debug is False
            
            # CORS origins should be parsed correctly
            origins = settings.cors_origins
            assert len(origins) == 2
            assert "http://localhost:3000" in origins
            assert "http://localhost:5173" in origins
    
    def test_case_insensitive_env_vars(self):
        """Test that environment variables remain case insensitive"""
        # Test with mixed case environment variables
        with patch.dict(os.environ, {'allowed_origins': 'http://localhost:4000,http://localhost:5000'}):
            settings = Settings()
            origins = settings.cors_origins
            
            # Should work with lowercase environment variable
            assert len(origins) == 2
            assert "http://localhost:4000" in origins
            assert "http://localhost:5000" in origins
    
    def test_no_breaking_changes_to_settings_interface(self):
        """Test that the Settings class interface hasn't changed in breaking ways"""
        settings = Settings()
        
        # All existing properties should still exist and be accessible
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'api_host')
        assert hasattr(settings, 'api_port')
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'allowed_origins')
        assert hasattr(settings, 'worker_api_key')
        assert hasattr(settings, 'cors_origins')
        
        # cors_origins should return a list (enhanced behavior)
        assert isinstance(settings.cors_origins, list)
        
        # allowed_origins should still be a string (backward compatibility)
        assert isinstance(settings.allowed_origins, str)
    
    def test_default_values_unchanged(self):
        """Test that default values for existing settings haven't changed"""
        # Create a temporary Settings class that doesn't read from .env file
        from pydantic_settings import BaseSettings
        from typing import Optional
        
        class TestSettings(BaseSettings):
            database_url: str = "sqlite:///./app.db"
            api_host: str = "0.0.0.0"
            api_port: int = 8000
            debug: bool = True
            allowed_origins: str = "http://localhost:3000,http://localhost:5173"
            worker_api_key: Optional[str] = None
            
            class Config:
                env_file = None  # Don't read from .env file
                case_sensitive = False
        
        # Clear environment to test true defaults
        with patch.dict(os.environ, {}, clear=True):
            settings = TestSettings()
            
            # Default values should remain the same
            assert settings.database_url == "sqlite:///./app.db"
            assert settings.api_host == "0.0.0.0"
            assert settings.api_port == 8000
            assert settings.debug is True
            assert settings.allowed_origins == "http://localhost:3000,http://localhost:5173"
            assert settings.worker_api_key is None
    
    def test_config_class_behavior_preserved(self):
        """Test that Config class behavior is preserved"""
        settings = Settings()
        
        # Config should still read from .env file
        assert hasattr(settings.Config, 'env_file')
        assert settings.Config.env_file == ".env"
        
        # Case sensitivity setting should be preserved
        assert hasattr(settings.Config, 'case_sensitive')
        assert settings.Config.case_sensitive is False
    
    def test_mixed_development_production_origins(self):
        """Test common scenario of mixing development and production origins"""
        # Common pattern: keep localhost for development, add production domain
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'http://localhost:5173,https://transcribe-frontend-jet.vercel.app'}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "http://localhost:5173" in origins
            assert "https://transcribe-frontend-jet.vercel.app" in origins
    
    def test_empty_string_fallback_behavior(self):
        """Test that empty string in environment variable falls back to defaults"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': ''}):
            settings = Settings()
            origins = settings.cors_origins
            
            # Should fall back to development defaults
            assert len(origins) == 2
            assert "http://localhost:3000" in origins
            assert "http://localhost:5173" in origins