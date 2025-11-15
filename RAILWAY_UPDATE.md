# Railway Deployment Update Instructions

## Important: Railway Root Directory

If Railway backend hasn't been updated, check the following:

### 1. Verify Railway Project Configuration

In Railway Dashboard:
1. Go to your project → **Settings** → **Source**
2. Verify **Root Directory** is set to `/` (root) or empty
3. If it's set to `frontend` or another directory, change it to `/` (root)

### 2. Verify Service Configuration

In Railway Dashboard:
1. Go to your project → **Settings** → **Service**
2. Check **Start Command** should be: `python3 backend_server.py`
3. Check **Build Command** should be: `pip install -r requirements.txt`

### 3. Force Redeploy

If files aren't updating:
1. Go to Railway Dashboard → **Deployments**
2. Click **"Redeploy"** on the latest deployment
3. Or trigger a new deployment by making a small commit

### 4. Check Railway is Watching Correct Files

Railway should detect changes to:
- `backend_server.py`
- `mcp_client_fastmcp.py`
- `requirements.txt`
- `Procfile`
- `railway.json`

### 5. Verify Environment Variables

In Railway Dashboard → **Variables**, ensure:
```
FINCHAT_MCP_URL=https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse
PORT=5001
DEBUG=False
```

### 6. Check Railway Logs

View logs to see what Railway is doing:
1. Railway Dashboard → **Deployments** → Click latest deployment
2. View **Build Logs** and **Deploy Logs**
3. Look for errors or warnings

### 7. Manual Trigger

If auto-deploy isn't working:
1. Railway Dashboard → **Settings** → **Source**
2. Click **"Redeploy"** or **"Trigger Deploy"**

## Files That Should Be Deployed

Railway should have access to these files in the root:
- ✅ `backend_server.py` - Main Flask server
- ✅ `mcp_client_fastmcp.py` - MCP client with retry logic
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Process definition
- ✅ `railway.json` - Railway configuration

## If Railway is in a Different Repository

If Railway is connected to a different GitHub repository:
1. Note the repository name
2. Push these files to that repository instead
3. Or reconnect Railway to `write-aid-mcp` repository

## Troubleshooting

### Railway Not Detecting Changes
- Check if Railway is connected to the correct GitHub branch (should be `main`)
- Verify Railway has access to the repository
- Try manually triggering a redeploy

### Build Fails
- Check `requirements.txt` has all dependencies
- Verify Python version (Railway uses Python 3.11+)
- Check build logs for specific errors

### Server Won't Start
- Verify `Procfile` has correct command: `web: python3 backend_server.py`
- Check `PORT` environment variable is set
- Verify `backend_server.py` exists and is executable

