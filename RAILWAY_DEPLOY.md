# Railway Deployment Guide

Quick guide to deploy the backend to Railway.

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. GitHub repository with your code
3. MCP URL configured

## Deployment Steps

### 1. Connect Repository to Railway

1. Go to [Railway Dashboard](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `write-aid-mcp` repository
5. Railway will auto-detect Python

### 2. Configure Environment Variables

In Railway dashboard → Your Project → Variables tab, add:

**Required:**
```bash
FINCHAT_MCP_URL=https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse
PORT=5001
DEBUG=False
```

**Optional:**
```bash
CORS_ORIGINS=https://your-frontend-domain.com,https://*.vercel.app
```

### 3. Deploy

Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Start the server using `Procfile`
3. Expose the service on a public URL

### 4. Get Your Backend URL

After deployment:
1. Go to your project → Settings → Networking
2. Generate a public domain
3. Copy the URL (e.g., `https://your-app.railway.app`)

### 5. Test Deployment

```bash
# Health check
curl https://your-app.railway.app/health

# Config check
curl https://your-app.railway.app/api/config

# Test MCP analyze (starts a job)
curl -X POST https://your-app.railway.app/api/mcp/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Test text", "purpose": "Testing"}'
```

### 6. Update Frontend

Update your frontend configuration to use the Railway URL:

```javascript
// In frontend/src/services/FinChatClient.js or ai_checker_config.js
this.backendUrl = 'https://your-app.railway.app'
```

## Files Created for Railway

- `backend_server.py` - Flask backend server
- `requirements.txt` - Python dependencies
- `Procfile` - Railway start command
- `railway.json` - Railway configuration

## Troubleshooting

### Deployment Fails

1. Check Railway logs: Project → Deployments → View logs
2. Verify `requirements.txt` has all dependencies
3. Check Python version (Railway uses Python 3.11+)

### MCP Not Working

1. Verify `FINCHAT_MCP_URL` is set correctly
2. Check logs for connection errors
3. Test MCP URL locally first

### CORS Errors

1. Add `CORS_ORIGINS` environment variable
2. Include your frontend domain
3. Redeploy after adding variable

### Port Issues

- Railway sets `PORT` automatically
- Backend reads from `PORT` environment variable
- Defaults to 5001 if not set

## Monitoring

View logs in Railway dashboard:
- Real-time logs: Project → Deployments → Logs
- Metrics: Project → Metrics tab

## Auto-Deploy

Railway automatically deploys when you push to GitHub:
```bash
git add .
git commit -m "Update backend"
git push origin main
```

Railway will detect changes and redeploy automatically.

