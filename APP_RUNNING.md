# ✅ App is Running!

## Current Status

✅ **Backend Server**: Running on http://localhost:5001  
✅ **Frontend Server**: Running on http://localhost:8000  
🌐 **Browser**: App should be open at http://localhost:8000/ai_checker.html

## ⚠️ Next Step: Configure Finchat Credentials

The backend is running but **finchat is not configured yet**. To link to finchat AI detector:

### Set Environment Variables

Open a terminal and run:

```bash
export FINCHAT_BASE_URL="https://your-finchat-instance.com"
export FINCHAT_API_TOKEN="your_jwt_token_here"
export FINCHAT_COT_SLUG="ai-detector"
export FINCHAT_MODEL="gemini-2.5-flash"
```

**Replace with your actual values:**
- `FINCHAT_BASE_URL`: Your finchat instance URL
- `FINCHAT_API_TOKEN`: Your JWT token from finchat
- `FINCHAT_COT_SLUG`: Your CoT slug (usually `ai-detector`)
- `FINCHAT_MODEL`: Model to use (default: `gemini-2.5-flash`)

### Restart Backend

After setting environment variables, restart the backend:

1. Find the backend process:
   ```bash
   ps aux | grep backend_server
   ```

2. Kill it:
   ```bash
   pkill -f backend_server.py
   ```

3. Restart with new environment:
   ```bash
   cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai/AI Checker2"
   python3 backend_server.py
   ```

### Verify Connection

Check backend health:
```bash
curl http://localhost:5001/health
```

Should show: `"finchat_configured": true`

Then refresh your browser - the app will automatically connect to finchat!

## Architecture

```
Browser → Backend (localhost:5001) → Finchat API
```

The frontend calls the backend, which securely handles all finchat API calls.

## See Also

- `FINCHAT_API_REQUIREMENTS.md` - Detailed information about what credentials you need
- `QUICK_SETUP.md` - Quick reference card


