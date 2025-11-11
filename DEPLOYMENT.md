# Deployment Guide: Vercel (Frontend) + Railway (Backend)

This guide walks you through deploying the AI Checker application with the frontend on Vercel and the backend on Railway.

## Architecture

```
Vercel (Frontend)                Railway (Backend)
┌─────────────────────┐          ┌──────────────────────┐
│ ai_checker.html     │          │ backend_server.py    │
│ ai_checker.js       │  ────►   │ (Flask + FastMCP)    │
│ ai_checker_config.js│          │                      │
└─────────────────────┘          └──────────────────────┘
                                           │
                                           ▼
                                  FinChat MCP Server
```

---

## Part 1: Deploy Backend to Railway

### Step 1: Create Railway Account
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `write-aid-mcp` repository
4. Railway will auto-detect the Python app

### Step 3: Configure Environment Variables
In Railway dashboard, go to **Variables** tab and add:

```bash
FINCHAT_MCP_URL=https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse
PORT=5001
DEBUG=False
```

**Optional (for REST API mode):**
```bash
FINCHAT_BASE_URL=https://finchat-api.adgo.dev
FINCHAT_API_TOKEN=your_jwt_token_here
FINCHAT_COT_SLUG=ai-detector
FINCHAT_MODEL=gemini-2.5-flash
```

### Step 4: Deploy
1. Railway will automatically deploy
2. Wait for deployment to complete
3. Click on the deployment to get your backend URL
4. It will look like: `https://your-app.railway.app`

### Step 5: Test Backend
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "finchat_configured": false,
  "timestamp": "2025-11-11T..."
}
```

Check MCP config:
```bash
curl https://your-app.railway.app/api/config
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Update Frontend Config
Before deploying, update the backend URL in `ai_checker_config.js`:

```javascript
BACKEND_URL: typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? 'https://your-app.railway.app'  // <-- Replace with your Railway URL
    : 'http://localhost:5001',
```

Commit this change:
```bash
git add ai_checker_config.js
git commit -m "Update backend URL for production"
git push origin main
```

### Step 2: Create Vercel Account
1. Go to [Vercel.com](https://vercel.com)
2. Sign up with GitHub

### Step 3: Import Project
1. Click "Add New..." → "Project"
2. Import your `write-aid-mcp` repository
3. Configure project:
   - **Framework Preset:** Other
   - **Root Directory:** `./` (leave as is)
   - **Build Command:** (leave empty - static site)
   - **Output Directory:** `./` (leave as is)

### Step 4: Configure Environment Variables (Optional)
In Vercel dashboard, go to **Settings** → **Environment Variables**:

```bash
BACKEND_URL=https://your-app.railway.app
```

If you want to use this, update `ai_checker_config.js`:
```javascript
BACKEND_URL: typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? (window.BACKEND_URL || process.env.BACKEND_URL || 'https://your-app.railway.app')
    : 'http://localhost:5001',
```

### Step 5: Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Your app will be live at: `https://your-app.vercel.app`

---

## Part 3: Configure CORS (if needed)

If you encounter CORS errors, update the backend to allow your Vercel domain.

Edit `backend_server.py`:

```python
from flask_cors import CORS

# Get allowed origins from environment
allowed_origins = os.getenv('CORS_ORIGINS', '*').split(',')

# Configure CORS
CORS(app, origins=allowed_origins)
```

Then set in Railway:
```bash
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app
```

---

## Part 4: Test Production Deployment

### Test 1: Access Frontend
1. Visit `https://your-app.vercel.app`
2. You should see the AI Checker interface

### Test 2: Check Connection Status
Look at the connection status in the header:
- ✅ **MCP Connected** - Backend is working
- ⚠️ **Backend Offline** - Check Railway deployment
- ❌ **Error** - Check browser console for errors

### Test 3: Run Analysis
1. Paste test text into the input
2. Click "GO"
3. Wait ~10 minutes for results
4. Results should appear in the right panel

### Test 4: Check Browser Console
Open Developer Tools → Console:
- Should show backend URL being used
- Should show "✓ Finchat client initialized (MCP mode)"
- No CORS errors

---

## Environment Variables Summary

### Railway Backend
**Required:**
```bash
FINCHAT_MCP_URL=https://finchat-api.adgo.dev/cot-mcp/YOUR_ID/sse
PORT=5001
DEBUG=False
```

**Optional:**
```bash
FINCHAT_BASE_URL=https://finchat-api.adgo.dev
FINCHAT_API_TOKEN=your_jwt_token
FINCHAT_COT_SLUG=ai-detector
FINCHAT_MODEL=gemini-2.5-flash
CORS_ORIGINS=https://your-app.vercel.app
```

### Vercel Frontend
**Optional:**
```bash
BACKEND_URL=https://your-app.railway.app
```

---

## Troubleshooting

### Issue: "Backend Offline" in frontend
**Solution:**
1. Check Railway deployment is running
2. Visit `https://your-railway-app.railway.app/health`
3. Check Railway logs for errors

### Issue: CORS Error
**Solution:**
1. Add CORS_ORIGINS to Railway environment variables
2. Include your Vercel domain
3. Redeploy Railway app

### Issue: MCP Not Configured
**Solution:**
1. Check FINCHAT_MCP_URL is set in Railway
2. Verify the MCP URL is correct
3. Check Railway logs for startup messages

### Issue: 502 Bad Gateway on Railway
**Solution:**
1. Check Railway logs for Python errors
2. Verify all required packages are in requirements.txt
3. Check PORT environment variable is set

### Issue: Frontend can't reach backend
**Solution:**
1. Verify backend URL in `ai_checker_config.js`
2. Check browser console for the URL being used
3. Make sure Railway app is not sleeping (upgrade plan if needed)

---

## Updating Deployments

### Update Backend (Railway)
```bash
git add backend_server.py
git commit -m "Update backend"
git push origin main
```
Railway will auto-deploy from GitHub.

### Update Frontend (Vercel)
```bash
git add ai_checker.html ai_checker.js ai_checker_config.js
git commit -m "Update frontend"
git push origin main
```
Vercel will auto-deploy from GitHub.

---

## Custom Domains (Optional)

### Vercel Custom Domain
1. Go to Vercel dashboard → Settings → Domains
2. Add your domain (e.g., `ai-checker.yourdomain.com`)
3. Update DNS records as instructed

### Railway Custom Domain
1. Go to Railway dashboard → Settings → Domains
2. Add your domain (e.g., `api.yourdomain.com`)
3. Update DNS records as instructed
4. Update `ai_checker_config.js` with new backend URL

---

## Monitoring

### Railway Logs
View real-time logs:
1. Railway dashboard → Your project
2. Click on "Deployments" tab
3. View logs for debugging

### Vercel Logs
View deployment logs:
1. Vercel dashboard → Your project
2. Click on "Deployments" tab
3. View build and runtime logs

---

## Cost

### Railway
- **Free tier:** $5 credit/month (enough for light usage)
- **Pro tier:** $20/month + usage

### Vercel
- **Hobby tier:** Free (personal projects)
- **Pro tier:** $20/month (commercial projects)

---

## Security Notes

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use environment variables** for all secrets
3. **FINCHAT_MCP_URL** contains your session ID - keep it secret
4. **Enable CORS** only for your domains
5. **Set DEBUG=False** in production

---

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Deploy frontend to Vercel
3. ✅ Test the integration
4. 🔜 Add custom domains (optional)
5. 🔜 Set up monitoring/alerts
6. 🔜 Add analytics (optional)

---

## Support

If you encounter issues:
1. Check Railway logs
2. Check Vercel logs
3. Check browser console
4. Review this deployment guide
5. Check `TROUBLESHOOTING.md` in the repo

