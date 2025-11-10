# MCP Integration Guide

## Overview

The AI Checker now supports **Model Context Protocol (MCP)** for connecting to FinChat. This provides a standardized way to interact with FinChat's AI detection capabilities.

## What is MCP?

MCP (Model Context Protocol) is a modern protocol for AI model interaction that provides:
- Standardized communication with LLM services
- Tool discovery and invocation
- Resource management
- Real-time streaming (via Server-Sent Events)

## Configuration

### Quick Start - Using MCP URL

The simplest way to use MCP is with your MCP endpoint URL:

```bash
export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
```

Then start the app:

```bash
./start_with_mcp.sh
```

### Manual Configuration

1. **Set MCP URL** (Required):
   ```bash
   export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/YOUR_SESSION_ID/sse"
   ```

2. **Set API Token** (if required):
   ```bash
   export FINCHAT_API_TOKEN="your_jwt_token"
   ```

3. **Start Backend**:
   ```bash
   python3 backend_server.py
   ```

4. **Start Frontend**:
   ```bash
   python3 -m http.server 8000
   ```

5. **Open in Browser**:
   ```
   http://localhost:8000/ai_checker.html
   ```

## MCP URL Format

Your MCP URL follows this structure:

```
https://finchat-api.adgo.dev/cot-mcp/{SESSION_ID}/sse
```

Where:
- **Base URL**: `https://finchat-api.adgo.dev`
- **Session ID**: Unique identifier for your MCP session (e.g., `68e8b27f658abfa9795c85da`)
- **Endpoint**: `/sse` (Server-Sent Events)

## How It Works

### MCP Mode Architecture

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Browser   │◄───────►│   Backend   │◄───────►│   FinChat    │
│  (Frontend) │         │ Flask Server│         │  MCP Server  │
└─────────────┘         └─────────────┘         └──────────────┘
     HTTP                    HTTP                    MCP/SSE
```

1. **Frontend** sends text to analyze to backend
2. **Backend** extracts session ID from MCP URL
3. **Backend** makes API call using MCP session
4. **FinChat** processes request and returns AI detection result
5. **Backend** forwards result to frontend
6. **Frontend** displays analysis

### Endpoints

When MCP is configured, the backend provides:

- **`/api/mcp/analyze`** - MCP-based text analysis (primary)
- **`/api/chat`** - REST API fallback
- **`/api/config`** - Configuration status
- **`/health`** - Health check

### API Example

**Request to `/api/mcp/analyze`:**

```javascript
POST http://localhost:5001/api/mcp/analyze
Content-Type: application/json

{
  "sentence": "The text to analyze",
  "paragraph": "Full paragraph context"
}
```

**Response:**

```json
{
  "success": true,
  "result": {
    "ai_generated": false,
    "confidence": 0.85,
    "analysis": "..."
  }
}
```

## Comparison: MCP vs REST API

| Feature | MCP Mode | REST API Mode |
|---------|----------|---------------|
| **Configuration** | Single MCP URL | Base URL + Token + CoT Slug |
| **Session Management** | Automatic (embedded in URL) | Manual (create session each time) |
| **Protocol** | MCP over SSE | HTTP REST |
| **Setup Complexity** | ✅ Simple | ⚠️ More complex |
| **Error Handling** | Built-in | Custom implementation |

## Troubleshooting

### MCP Not Working

1. **Check Configuration**:
   ```bash
   curl http://localhost:5001/api/config
   ```
   
   Should show:
   ```json
   {
     "mcp_enabled": true,
     "mcp_session_id": "68e8b27f658abfa9795c85da",
     "mcp_url": "https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
   }
   ```

2. **Test Health Endpoint**:
   ```bash
   curl http://localhost:5001/health
   ```

3. **Check Backend Logs**:
   Look for:
   ```
   ✓ MCP Mode Enabled
   Base URL: https://finchat-api.adgo.dev
   MCP Session ID: 68e8b27f658abfa9795c85da
   ```

### Common Issues

#### "MCP not configured" Error

**Problem**: `FINCHAT_MCP_URL` environment variable not set.

**Solution**:
```bash
export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/YOUR_ID/sse"
```

#### HTTP 400/404 Errors

**Problem**: MCP endpoint URL incorrect or session expired.

**Solution**: 
- Verify MCP URL is correct
- Check if session ID is still valid
- Try regenerating MCP URL from FinChat

#### Connection Timeout

**Problem**: MCP server not responding.

**Solution**:
- Check internet connection
- Verify FinChat server is accessible
- Try REST API mode as fallback

## Fallback to REST API

If MCP fails, the system can fall back to REST API mode:

1. **Disable MCP** in `ai_checker_config.js`:
   ```javascript
   USE_MCP: false
   ```

2. **Configure REST API**:
   ```bash
   export FINCHAT_BASE_URL="https://your-finchat.com"
   export FINCHAT_API_TOKEN="your_token"
   export FINCHAT_COT_SLUG="ai-detector"
   ```

3. **Restart Backend**:
   ```bash
   python3 backend_server.py
   ```

## Files Modified for MCP Support

- **`backend_server.py`** - Added MCP endpoint and session ID extraction
- **`ai_checker_config.js`** - Added MCP configuration options
- **`mcp_finchat_client.py`** - MCP protocol client implementation
- **`start_with_mcp.sh`** - MCP-enabled startup script
- **`requirements.txt`** - Added MCP dependencies

## Dependencies

MCP mode requires:
- `mcp>=0.9.0` - MCP protocol library
- `httpx>=0.26.0` - Modern HTTP client
- `httpx-sse>=0.4` - SSE support

Install with:
```bash
pip3 install -r requirements.txt
```

## Security Notes

### MCP URL Security

- MCP URL contains session ID - treat as sensitive
- Don't commit MCP URLs to version control
- Use environment variables for configuration
- Rotate session IDs periodically

### Backend Security

- Backend keeps tokens server-side (not exposed to frontend)
- CORS enabled for localhost development only
- For production: configure CORS properly and use HTTPS

## Next Steps

1. ✅ Get your MCP URL from FinChat
2. ✅ Set `FINCHAT_MCP_URL` environment variable  
3. ✅ Run `./start_with_mcp.sh`
4. ✅ Test analysis in the browser
5. 📝 Document any custom tool configurations
6. 🔒 Secure your MCP URL and tokens

## Support

For issues:
1. Check backend logs
2. Verify configuration with `/api/config`
3. Test health endpoint
4. Review `TROUBLESHOOTING.md`
5. Try REST API fallback

## References

- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [FinChat MCP GitHub](https://github.com/MikeVenge/mcp-finchat)
- Original MCP URL: `https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse`


