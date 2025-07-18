# Design Document

## Overview

This design enhances the existing CORS configuration in the FastAPI transcription backend to support flexible, environment-based origin management. The solution builds upon the current Pydantic Settings configuration pattern already established in the codebase, ensuring consistency with existing architecture while adding production-ready CORS handling for the Vercel frontend deployment.

## Architecture

The design leverages the existing `Settings` class in `app/config.py` which already uses Pydantic BaseSettings for environment variable management. The CORS configuration will be enhanced to:

1. **Environment Variable Processing**: Improve the existing `allowed_origins` field and `cors_origins` property to handle production domains
2. **Validation and Logging**: Add validation for origin formats and startup logging for transparency
3. **Backward Compatibility**: Maintain existing development workflow while supporting production deployments

## Components and Interfaces

### Enhanced Settings Configuration

The existing `Settings` class will be updated with:

```python
class Settings(BaseSettings):
    # Enhanced CORS configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse and validate CORS origins from environment variable"""
        # Enhanced parsing with validation and logging
```

### CORS Middleware Integration

The FastAPI CORS middleware configuration in `app/main.py` remains unchanged, continuing to use `settings.cors_origins` as the source of allowed origins.

### Environment Variable Structure

The `ALLOWED_ORIGINS` environment variable will support:
- Comma-separated list of origins
- Automatic whitespace trimming
- Support for both HTTP and HTTPS protocols
- Validation of URL format

## Data Models

### Configuration Schema

```python
# Input: Environment Variable
ALLOWED_ORIGINS="http://localhost:5173,https://transcribe-frontend-jet.vercel.app"

# Output: Parsed List
cors_origins = [
    "http://localhost:5173",
    "https://transcribe-frontend-jet.vercel.app"
]
```

### Validation Rules

- Origins must be valid URLs with protocol (http/https)
- No trailing slashes allowed
- Whitespace around commas is automatically trimmed
- Empty origins are filtered out

## Error Handling

### Configuration Errors

1. **Invalid URL Format**: Log warning and skip invalid origins
2. **Empty Configuration**: Fall back to development defaults
3. **Malformed Environment Variable**: Log error and use defaults

### Runtime CORS Errors

The existing FastAPI CORS middleware handles runtime CORS validation. Our enhancement focuses on configuration-time validation and logging.

### Error Logging Strategy

```python
# Startup logging for transparency
logger.info(f"CORS configured with origins: {settings.cors_origins}")

# Warning for invalid origins
logger.warning(f"Skipping invalid origin: {invalid_origin}")
```

## Testing Strategy

### Unit Tests

1. **Settings Configuration Tests**
   - Test default origin parsing
   - Test environment variable override
   - Test whitespace handling
   - Test invalid URL handling

2. **CORS Origin Validation Tests**
   - Test valid origin formats
   - Test invalid origin filtering
   - Test empty configuration handling

### Integration Tests

1. **CORS Middleware Tests**
   - Test allowed origin requests succeed
   - Test disallowed origin requests fail
   - Test preflight OPTIONS requests

### Manual Testing

1. **Development Environment**
   - Verify localhost origins work
   - Test with .env file configuration

2. **Production Environment**
   - Deploy to Railway with Vercel domain
   - Verify frontend can make API calls
   - Test CORS headers in browser network tab

## Implementation Considerations

### Backward Compatibility

- Existing development setup continues to work without changes
- Default values remain the same for local development
- .env file configuration pattern is preserved

### Security

- Explicit origin allowlist (no wildcards)
- URL validation prevents malformed origins
- Logging provides audit trail of configured origins

### Performance

- Origin parsing happens once at startup
- No runtime performance impact
- Minimal memory overhead for origin list

### Deployment

- Railway environment variables can be set through dashboard
- No code changes required for different environments
- Configuration changes require application restart