# Quick Start Guide - Running with Finchat Backend

## Current Status

✅ **Dependencies installed** (Flask, flask-cors, requests)  
✅ **Backend server running** on http://localhost:5000  
✅ **Frontend server running** on http://localhost:8000  
🌐 **Browser opened** to http://localhost:8000/ai_checker.html

## ⚠️ Important: Configure Finchat Credentials

The backend is running but **finchat is not configured yet**. You need to set environment variables:

### Step 1: Set Environment Variables

Open a new terminal and run:

```bash
export FINCHAT_BASE_URL="https://your-finchat-instance.com"
export FINCHAT_API_TOKEN="your_jwt_token_here"
export FINCHAT_COT_SLUG="ai-detector"
export FINCHAT_MODEL="gemini-2.5-flash"
```

### Step 2: Restart Backend

After setting environment variables, restart the backend:

```bash
# Stop current backend (Ctrl+C in the terminal running it)
# Then restart:
cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai/AI Checker2"
python3 backend_server.py
```

### Step 3: Verify Connection

Check backend health:
```bash
curl http://localhost:5000/health
```

Should show: `"finchat_configured": true`

## Alternative: Use the Start Script

You can also use the convenience script (after setting env vars):

```bash
./start_with_backend.sh
```

## What's Running

- **Backend**: http://localhost:5000 (Flask proxy server)
- **Frontend**: http://localhost:8000/ai_checker.html (Static web app)

## Next Steps

1. Set your finchat credentials as environment variables
2. Restart the backend server
3. Refresh the browser page
4. The app will automatically connect to finchat via the backend

See `FINCHAT_API_REQUIREMENTS.md` for detailed information about what credentials you need.


