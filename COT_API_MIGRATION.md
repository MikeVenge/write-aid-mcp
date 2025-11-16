# Migration from MCP to COT API

## Summary

The backend has been migrated from MCP (Model Context Protocol) to FinChat COT REST API for better stability and reliability.

## Changes Made

### Backend Changes

1. **New COT Client** (`cot_client.py`)
   - Implements FinChat COT REST API calls
   - Handles session creation, COT execution, polling, and result retrieval
   - Uses `ai-detector-v2` COT by default

2. **Updated Backend Server** (`backend_server.py`)
   - Removed MCP client dependency
   - Now uses COT API client
   - Same API endpoints (backward compatible)
   - Improved progress tracking

3. **Updated Dependencies** (`requirements.txt`)
   - Removed `fastmcp`
   - Added `requests` for HTTP calls

### Frontend Changes

- Updated to support both `mcp_enabled` and `cot_enabled` config flags
- Displays COT slug in console logs

## Environment Variables

### Required for Railway

Update your Railway environment variables:

**Remove:**
- `FINCHAT_MCP_URL` (no longer needed)

**Add/Update:**
```bash
FINCHAT_BASE_URL=https://finchat-api.adgo.dev
FINCHAT_API_TOKEN=your_jwt_token_here
COT_SLUG=ai-detector-v2
PORT=5001
DEBUG=False
```

### Optional
```bash
CORS_ORIGINS=https://your-frontend-domain.com
```

## API Endpoints (Unchanged)

The API endpoints remain the same for backward compatibility:

- `POST /api/mcp/analyze` - Start analysis job
- `GET /api/mcp/status/<job_id>` - Get job status
- `GET /health` - Health check
- `GET /api/config` - Configuration status

## How It Works

1. **Client sends request** → `POST /api/mcp/analyze` with `text` and `purpose`
2. **Backend creates job** → Returns `job_id` immediately
3. **Background processing**:
   - Creates FinChat session
   - Runs COT: `cot ai-detector-v2 $text:... $purpose:...`
   - Polls for completion
   - Retrieves results
4. **Client polls status** → `GET /api/mcp/status/<job_id>`
5. **Returns results** → When status is `completed`

## Testing

### Local Testing

```bash
# Set environment variables
export FINCHAT_BASE_URL="https://finchat-api.adgo.dev"
export FINCHAT_API_TOKEN="your_token_here"
export COT_SLUG="ai-detector-v2"

# Start backend
python3 backend_server.py

# Test health
curl http://localhost:5001/health

# Test config
curl http://localhost:5001/api/config

# Test analysis
curl -X POST http://localhost:5001/api/mcp/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Test text", "purpose": "Testing"}'
```

### Railway Testing

After updating environment variables in Railway:

```bash
# Health check
curl https://your-railway-url.railway.app/health

# Config check
curl https://your-railway-url.railway.app/api/config
```

## Benefits

1. **More Stable** - REST API is more reliable than MCP SSE connections
2. **Better Error Handling** - Standard HTTP status codes and error responses
3. **Progress Tracking** - Real-time progress updates via metadata
4. **Easier Debugging** - Standard HTTP requests can be inspected with tools like curl
5. **No Connection Issues** - No need to maintain persistent SSE connections

## Migration Checklist

- [x] Create COT client (`cot_client.py`)
- [x] Update backend server to use COT API
- [x] Update requirements.txt
- [x] Update frontend to support COT config
- [x] Push to backend branch
- [ ] Update Railway environment variables
- [ ] Test Railway deployment
- [ ] Verify analysis works end-to-end

## Troubleshooting

### "COT API not configured" Error

Make sure these environment variables are set in Railway:
- `FINCHAT_BASE_URL`
- `FINCHAT_API_TOKEN`

### "COT execution failed" Error

- Check that `FINCHAT_API_TOKEN` is valid
- Verify `FINCHAT_BASE_URL` is correct (no trailing slash)
- Check Railway logs for detailed error messages

### Analysis Takes Too Long

- COT analysis typically takes 8-10 minutes
- Check progress via status endpoint
- Increase polling timeout if needed

