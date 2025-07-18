import pytest
import os
from unittest.mock import patch
from app.config import Settings


class TestCORSConfiguration:
    """Test suite for CORS configuration parsing and validation"""
    
    def test_default_cors_origins(self):
        """Test that default origins are parsed correctly"""
        settings = Settings()
        origins = settings.cors_origins
        
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
        assert "http://localhost:5173" in origins
    
    def test_custom_cors_origins_from_env(self):
        """Test parsing custom origins from environment variable"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'https://example.com,http://localhost:8080'}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "https://example.com" in origins
            assert "http://localhost:8080" in origins
    
    def test_whitespace_handling(self):
        """Test that whitespace around commas is properly trimmed"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': ' https://example.com , http://localhost:8080 '}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "https://example.com" in origins
            assert "http://localhost:8080" in origins
    
    def test_empty_origins_filtered(self):
        """Test that empty origins are filtered out"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'https://example.com,,http://localhost:8080,'}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "https://example.com" in origins
            assert "http://localhost:8080" in origins
    
    def test_invalid_url_format_filtered(self):
        """Test that invalid URL formats are filtered out with warning"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'https://example.com,invalid-url,http://localhost:8080'}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "https://example.com" in origins
            assert "http://localhost:8080" in origins
    
    def test_unsupported_scheme_filtered(self):
        """Test that unsupported schemes are filtered out"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'https://example.com,ftp://example.com,http://localhost:8080'}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "https://example.com" in origins
            assert "http://localhost:8080" in origins
    
    def test_missing_scheme_filtered(self):
        """Test that URLs without scheme are filtered out"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'https://example.com,example.com,http://localhost:8080'}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "https://example.com" in origins
            assert "http://localhost:8080" in origins
    
    def test_trailing_slash_removed(self):
        """Test that trailing slashes are removed for consistency"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'https://example.com/,http://localhost:8080/'}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "https://example.com" in origins
            assert "http://localhost:8080" in origins
    
    def test_fallback_to_defaults_on_all_invalid(self):
        """Test fallback to development defaults when all origins are invalid"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'invalid-url,ftp://example.com,not-a-url'}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "http://localhost:3000" in origins
            assert "http://localhost:5173" in origins
    
    def test_empty_environment_variable(self):
        """Test behavior with empty environment variable"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': ''}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "http://localhost:3000" in origins
            assert "http://localhost:5173" in origins
    
    def test_production_vercel_domain(self):
        """Test parsing production Vercel domain"""
        with patch.dict(os.environ, {'ALLOWED_ORIGINS': 'http://localhost:5173,https://transcribe-frontend-jet.vercel.app'}):
            settings = Settings()
            origins = settings.cors_origins
            
            assert len(origins) == 2
            assert "http://localhost:5173" in origins
            assert "https://transcribe-frontend-jet.vercel.app" in origins