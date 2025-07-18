import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


class TestCORSIntegration:
    """Integration tests for CORS middleware behavior"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_allowed_origin_request_succeeds(self):
        """Test that requests from allowed origins succeed with proper CORS headers"""
        # Test with default localhost origin
        response = self.client.get(
            "/health",
            headers={"Origin": "http://localhost:5173"}
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    
    def test_disallowed_origin_request_fails(self):
        """Test that requests from disallowed origins are rejected"""
        response = self.client.get(
            "/health",
            headers={"Origin": "https://malicious-site.com"}
        )
        
        # Request succeeds but CORS headers are not set for disallowed origin
        assert response.status_code == 200
        # FastAPI CORS middleware doesn't set the header for disallowed origins
        assert response.headers.get("access-control-allow-origin") != "https://malicious-site.com"
    
    def test_preflight_options_request_allowed_origin(self):
        """Test preflight OPTIONS requests work correctly for allowed origins"""
        response = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_preflight_options_request_disallowed_origin(self):
        """Test preflight OPTIONS requests are rejected for disallowed origins"""
        response = self.client.options(
            "/health",
            headers={
                "Origin": "https://malicious-site.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # FastAPI CORS middleware rejects preflight requests from disallowed origins with 400
        assert response.status_code == 400
        assert response.headers.get("access-control-allow-origin") != "https://malicious-site.com"
    
    @patch.dict(os.environ, {'ALLOWED_ORIGINS': 'https://example.com,http://localhost:8080'})
    def test_custom_origins_from_environment(self):
        """Test that custom origins from environment variables work correctly"""
        # Need to reload the app with new environment
        from importlib import reload
        from app import config, main
        reload(config)
        reload(main)
        
        client = TestClient(main.app)
        
        # Test allowed custom origin
        response = client.get(
            "/health",
            headers={"Origin": "https://example.com"}
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "https://example.com"
        
        # Test that default origins are no longer allowed
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:5173"}
        )
        
        assert response.status_code == 200
        # Should not have CORS header for origin not in custom list
        assert response.headers.get("access-control-allow-origin") != "http://localhost:5173"
    
    def test_cors_credentials_allowed(self):
        """Test that CORS credentials are properly configured"""
        response = self.client.get(
            "/health",
            headers={"Origin": "http://localhost:5173"}
        )
        
        assert response.status_code == 200
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"
    
    def test_cors_methods_allowed(self):
        """Test that all HTTP methods are allowed via CORS"""
        response = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-methods" in response.headers
        # Should allow all methods (*)
        allowed_methods = response.headers["access-control-allow-methods"]
        assert "POST" in allowed_methods or "*" in allowed_methods
    
    def test_cors_headers_allowed(self):
        """Test that all headers are allowed via CORS"""
        response = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-headers" in response.headers
        # Should allow all headers (*)
        allowed_headers = response.headers["access-control-allow-headers"]
        assert "content-type" in allowed_headers.lower() or "*" in allowed_headers
    
    def test_no_origin_header_request(self):
        """Test that requests without Origin header work normally"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        # No CORS headers should be set when no Origin header is present
        assert "access-control-allow-origin" not in response.headers