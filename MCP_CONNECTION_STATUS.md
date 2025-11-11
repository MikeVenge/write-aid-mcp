# MCP Connection Status

## ✅ Connected to FinChat MCP

**Status**: Active  
**Date Connected**: November 10, 2025

---

## 🔗 Connection Details

### MCP Endpoint
- **URL**: `https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse`
- **Session ID**: `68e8b27f658abfa9795c85da`
- **Protocol**: Server-Sent Events (SSE)
- **Base URL**: `https://finchat-api.adgo.dev`

### Configuration
- **Model**: `gemini-2.5-flash`
- **CoT Slug**: `ai-detector`
- **Backend Port**: `5001`
- **Frontend Port**: `8000`

---

## 🚀 How to Use

### 1. Start Backend with MCP
```bash
./start_backend_with_mcp.sh
```

Or manually:
```bash
export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
python3 backend_server.py
```

### 2. Start Frontend
```bash
python3 -m http.server 8000
```

### 3. Access the App
Open browser to: http://localhost:8000/ai_checker.html

---

## 🔧 API Endpoints

### Check MCP Configuration
```bash
curl http://localhost:5001/api/config
```

**Response**:
```json
{
  "configured": false,
  "base_url": "https://finchat-api.adgo.dev",
  "cot_slug": "ai-detector",
  "model": "gemini-2.5-flash",
  "mcp_enabled": true,
  "mcp_session_id": "68e8b27f658abfa9795c85da",
  "mcp_url": "https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
}
```

### Health Check
```bash
curl http://localhost:5001/health
```

### Analyze Text via MCP
```bash
curl -X POST http://localhost:5001/api/mcp/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "sentence": "Your text here",
    "paragraph": "Full context here",
    "purpose": "AI detection for content analysis"
  }'
```

---

## 📋 Architecture

```
┌─────────────┐         ┌─────────────┐         ┌──────────────────┐
│   Browser   │────────▶│   Backend   │────────▶│   FinChat MCP    │
│  (Port 8000)│         │  (Port 5001)│         │   (SSE Stream)   │
└─────────────┘         └─────────────┘         └──────────────────┘
      ▲                        │                         │
      │                        │                         │
      │                        ▼                         ▼
      │                  MCP Protocol            ai-detector CoT
      │                  (FastMCP)              (gemini-2.5-flash)
      │                        │                         │
      └────────────────────────┴─────────────────────────┘
                         Analysis Results
```

### Flow:
1. User pastes text in frontend
2. Frontend sends to backend `/api/mcp/analyze`
3. Backend uses MCP client to connect to FinChat
4. FinChat processes via `ai-detector` CoT
5. Results stream back via SSE
6. Backend returns analysis to frontend
7. Frontend displays results

---

## 🔐 Security Notes

- MCP URL contains session authentication
- No API tokens exposed in frontend
- All FinChat communication proxied through backend
- Session ID embedded in MCP URL for authentication

---

## 🛠️ Troubleshooting

### Backend Not Connecting to MCP
```bash
# Check if MCP URL is set
curl http://localhost:5001/api/config | grep mcp_enabled

# Should show: "mcp_enabled": true
```

### Restart Backend with MCP
```bash
pkill -f "backend_server.py"
./start_backend_with_mcp.sh
```

### Test MCP Connection
```bash
curl -X POST http://localhost:5001/api/mcp/analyze \
  -H "Content-Type: application/json" \
  -d '{"sentence":"Test text","paragraph":"Testing MCP"}'
```

---

## 📝 Environment Variables

Set these when starting the backend:

```bash
export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
export FINCHAT_MODEL="gemini-2.5-flash"
export FINCHAT_COT_SLUG="ai-detector"
```

Or use the provided script: `./start_backend_with_mcp.sh`

---

## ✅ Verification Checklist

- [x] MCP URL configured
- [x] Backend server running on port 5001
- [x] Frontend server running on port 8000
- [x] MCP enabled in backend config
- [x] Session ID extracted from URL
- [x] ai-detector CoT available
- [x] gemini-2.5-flash model configured

---

## 🎯 Next Steps

1. Test the connection by analyzing sample text
2. Monitor MCP responses for accuracy
3. Adjust CoT parameters if needed
4. Deploy to production environment
5. Set up monitoring and logging

---

**Last Updated**: November 10, 2025  
**Connection**: Active ✅  
**Endpoint**: https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse

