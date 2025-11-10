# Why Backend Wasn't Linking to Finchat API

## The Problem

**There was NO backend** - the app was frontend-only, making direct API calls from the browser to finchat.

## Why It Failed

1. **No Backend Server**: The `python3 -m http.server` is just a static file server, not a backend API
2. **Direct Browser Calls**: JavaScript tried to call finchat directly, which caused:
   - **CORS errors** (browser blocks cross-origin requests)
   - **Security issues** (API tokens exposed in browser)
   - **Configuration problems** (placeholder values in config file)

## The Solution

I've created a **backend proxy server** (`backend_server.py`) that:

✅ **Keeps tokens secure** - API credentials stay on the server  
✅ **Handles CORS** - Backend makes requests, browser only talks to backend  
✅ **Proper error handling** - Clear messages when finchat isn't configured  
✅ **Health checks** - Frontend can verify backend is running and configured

## New Architecture

```
Browser → Backend Server (Flask) → finchat API
```

Instead of:
```
Browser → finchat API (direct, insecure, CORS issues)
```

## How to Use

### 1. Configure Backend

Set environment variables:
```bash
export FINCHAT_BASE_URL="https://your-finchat-instance.com"
export FINCHAT_API_TOKEN="your_jwt_token_here"
export FINCHAT_COT_SLUG="ai-detector"
export FINCHAT_MODEL="gemini-2.5-flash"
```

### 2. Install Dependencies

```bash
pip3 install flask flask-cors requests
```

### 3. Start Backend

```bash
python3 backend_server.py
```

Backend runs on `http://localhost:5000`

### 4. Start Frontend

```bash
python3 -m http.server 8000
```

Or use the convenience script:
```bash
./start_with_backend.sh
```

## Files Changed

- ✅ `backend_server.py` - New Flask backend proxy
- ✅ `ai_checker.js` - Updated to call backend instead of finchat directly
- ✅ `ai_checker_config.js` - Now uses `BACKEND_URL` instead of `BASE_URL` and `API_TOKEN`
- ✅ `start_with_backend.sh` - Convenience script to start both servers

## Verification

Check backend health:
```bash
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "ok",
  "finchat_configured": true,
  "timestamp": "..."
}
```



