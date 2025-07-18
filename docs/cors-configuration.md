# CORS Configuration Guide

## Overview

The backend API uses environment-based CORS configuration to control which frontend domains can access the API. This allows for flexible deployment across different environments without code changes.

## Environment Variable Configuration

### ALLOWED_ORIGINS

The `ALLOWED_ORIGINS` environment variable accepts a comma-separated list of allowed origins.

**Format:**
```
ALLOWED_ORIGINS=origin1,origin2,origin3
```

**Examples:**

Development (default):
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Production with Vercel frontend:
```
ALLOWED_ORIGINS=http://localhost:5173,https://transcribe-frontend-jet.vercel.app
```

Multiple production domains:
```
ALLOWED_ORIGINS=https://app.transcribe.cafe,https://transcribe-frontend-jet.vercel.app,https://staging.transcribe.cafe
```

## Railway Deployment Configuration

To configure CORS origins in Railway:

1. Go to your Railway project dashboard
2. Navigate to the "Variables" tab
3. Add a new environment variable:
   - **Name:** `ALLOWED_ORIGINS`
   - **Value:** `http://localhost:5173,https://your-frontend-domain.vercel.app`
4. Deploy your changes

The backend will automatically use these origins for CORS configuration on startup.

## Validation and Error Handling

The backend automatically validates all origins and:

- ✅ Accepts HTTP and HTTPS protocols
- ✅ Trims whitespace around commas
- ✅ Filters out empty origins
- ✅ Removes trailing slashes for consistency
- ❌ Rejects invalid URL formats
- ❌ Rejects unsupported protocols (FTP, etc.)
- ❌ Rejects URLs without proper scheme/domain

If all origins are invalid, the backend falls back to development defaults (`localhost:3000` and `localhost:5173`).

## Logging

The backend logs CORS configuration on startup for verification:

```
INFO: CORS configured with origins: ['http://localhost:5173', 'https://transcribe-frontend-jet.vercel.app']
```

Invalid origins generate warning logs:
```
WARNING: Skipping invalid origin (missing scheme or netloc): example.com
WARNING: Skipping invalid origin (unsupported scheme): ftp://example.com
```

## Testing CORS Configuration

### Local Testing

1. Set `ALLOWED_ORIGINS` in your `.env` file
2. Start the backend server
3. Check the startup logs for configured origins
4. Test API calls from your frontend

### Production Testing

1. Deploy backend to Railway with `ALLOWED_ORIGINS` environment variable
2. Deploy frontend to Vercel (or your hosting platform)
3. Test API calls from the deployed frontend
4. Check Railway logs for CORS configuration confirmation

### Browser Developer Tools

You can verify CORS headers in your browser's Network tab:
- Look for `Access-Control-Allow-Origin` header in API responses
- Preflight OPTIONS requests should return appropriate CORS headers
- CORS errors will appear in the browser console if origins are not allowed

## Troubleshooting

**Frontend can't connect to backend:**
1. Check that your frontend domain is included in `ALLOWED_ORIGINS`
2. Verify the exact domain format (including protocol and port)
3. Check Railway logs for CORS configuration and any warning messages
4. Ensure there are no trailing slashes in the origin URLs

**CORS errors in browser console:**
1. Verify the `Access-Control-Allow-Origin` header in network responses
2. Check that the request origin matches exactly what's configured
3. For localhost development, ensure the port numbers match

**Backend falls back to development defaults:**
1. Check that `ALLOWED_ORIGINS` environment variable is set correctly
2. Verify there are no typos in the environment variable name
3. Check Railway logs for validation warnings about invalid origins