# How to Fix Frontend-Backend MCP Connection

## Problem
Frontend shows "⚠️ Finchat not configured" even though backend is running with MCP enabled.

## Solution - 3 Simple Steps

### Step 1: Open Test Page

Open this URL in your browser:
```
http://localhost:8000/test_mcp_frontend.html
```

This will run automatic tests to verify:
- ✅ Backend is running
- ✅ MCP is configured
- ✅ Connection is working

### Step 2: Hard Refresh Main App

Go to the main app:
```
http://localhost:8000/ai_checker.html
```

**Hard refresh** to clear cache:
- **Mac**: `Cmd + Shift + R`
- **Windows/Linux**: `Ctrl + Shift + R`

### Step 3: Verify Connection Status

After refreshing, look at the top-right of the page.

You should see: **"✅ MCP Connected"** (in green)

If you see this, the connection is working! 🎉

---

## What Was Fixed

### 1. ✅ Port Mismatch Fixed
- Changed frontend from port 5000 → 5001
- Now matches backend port

### 2. ✅ MCP Detection Added
- Frontend now checks `/api/config` for `mcp_enabled`
- Recognizes MCP mode automatically

### 3. ✅ Visual Status Indicator
- Added connection status in header
- Shows real-time MCP connection state

### 4. ✅ MCP Analysis Method
- Added `analyzeMCP()` function
- GO button now uses MCP when available
- Shows "Analyzing with AI Detector (MCP)..."

---

## Connection Status Indicators

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ MCP Connected | Working! | Ready to analyze text |
| ⚠️ Not Configured | Backend running, MCP not set | Set FINCHAT_MCP_URL |
| ⚠️ Backend Offline | Can't reach backend | Start backend_server.py |
| ❌ Error | Connection error | Check console for details |

---

## Troubleshooting

### If you still see "Not Configured":

**Option A: Check Backend**
```bash
curl http://localhost:5001/api/config | python3 -m json.tool
```

Look for:
```json
{
  "mcp_enabled": true,
  "mcp_session_id": "68e8b27f658abfa9795c85da"
}
```

If `mcp_enabled: false`, restart backend with MCP URL:
```bash
export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
python3 backend_server.py
```

**Option B: Clear Browser Cache**
1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

**Option C: Check Console**
1. Open browser console (F12 → Console tab)
2. Look for errors
3. Should see: "✓ Finchat client initialized (MCP mode)"

### If backend won't start:

Check if port is already in use:
```bash
lsof -ti:5001 | xargs kill -9
python3 backend_server.py
```

### If connection keeps failing:

1. **Verify files are updated:**
   ```bash
   cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai/AI Checker2"
   grep -n "MCP Connected" ai_checker.js
   ```
   Should find the line with "MCP Connected"

2. **Check if frontend server is running:**
   ```bash
   curl http://localhost:8000/ai_checker.html | head -5
   ```
   Should return HTML

3. **Test MCP endpoint directly:**
   ```bash
   curl -X POST http://localhost:5001/api/mcp/analyze \
     -H "Content-Type: application/json" \
     -d '{"sentence":"test","paragraph":"test"}' \
     --max-time 5
   ```
   Should accept the request (may timeout, that's ok)

---

## What Should Happen When Working

### 1. On Page Load:
- Connection status shows "Checking backend..."
- Then changes to "Checking MCP config..."
- Finally shows "✅ MCP Connected" (green)

### 2. In Console (F12):
```
✓ Finchat client initialized (MCP mode)
  Backend URL: http://localhost:5001
  MCP Session ID: 68e8b27f658abfa9795c85da
```

### 3. When You Click GO:
- Status shows: "Analyzing with AI Detector (MCP)... This may take ~10 minutes."
- Button disables during analysis
- After ~10 minutes: Results appear

---

## How MCP Works in This App

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│  Browser    │         │  Backend    │         │  FinChat     │
│  (Port 8000)│◄───────►│ (Port 5001) │◄───────►│  MCP Server  │
└─────────────┘         └─────────────┘         └──────────────┘
       │                       │                        │
       │ 1. POST /api/mcp/analyze                      │
       │──────────────────────►│                        │
       │                       │ 2. fastmcp.Client()   │
       │                       │   .call_tool()         │
       │                       │───────────────────────►│
       │                       │                        │
       │                       │   3. ai_detector      │
       │                       │      processing       │
       │                       │      (~10 minutes)    │
       │                       │                        │
       │                       │   4. Result           │
       │   5. Display result   │◄───────────────────────│
       │◄──────────────────────│                        │
```

---

## Quick Command Reference

**Start Backend with MCP:**
```bash
cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai/AI Checker2"
export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
python3 backend_server.py
```

**Start Frontend:**
```bash
cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai/AI Checker2"
python3 -m http.server 8000
```

**Or use startup script:**
```bash
./start_with_mcp.sh
```

**Test Connection:**
```
http://localhost:8000/test_mcp_frontend.html
```

**Main App:**
```
http://localhost:8000/ai_checker.html
```

---

## Files Updated

1. ✅ `ai_checker.html` - Added connection status indicator
2. ✅ `ai_checker.js` - Added MCP support and visual feedback
3. ✅ `ai_checker_config.js` - MCP configuration
4. ✅ `backend_server.py` - MCP endpoint
5. ✅ `mcp_client_fastmcp.py` - MCP client
6. ✅ `test_mcp_frontend.html` - Test page (NEW)

---

## Success Checklist

- [ ] Backend shows "✓ MCP Mode Enabled" on startup
- [ ] Test page shows all tests passing
- [ ] Main app shows "✅ MCP Connected" in header
- [ ] Console shows "✓ Finchat client initialized (MCP mode)"
- [ ] Clicking GO shows MCP analysis message
- [ ] No "Finchat not configured" warnings

If all checkboxes are ✅, your MCP connection is working perfectly! 🎉

---

## Need More Help?

1. Run the test page: `http://localhost:8000/test_mcp_frontend.html`
2. Check browser console (F12)
3. Check backend terminal output
4. Review `STATUS_CHECK.md` for detailed status
5. Review `MCP_IMPLEMENTATION_COMPLETE.md` for full documentation


