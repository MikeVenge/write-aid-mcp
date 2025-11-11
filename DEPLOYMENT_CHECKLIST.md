# Deployment Checklist

Use this checklist to ensure smooth deployment to Vercel and Railway.

## Pre-Deployment

- [ ] Ensure all code is committed to GitHub
- [ ] Test locally with `python3 backend_server.py`
- [ ] Test frontend by opening `ai_checker.html`
- [ ] Verify MCP connection works locally
- [ ] Review `requirements.txt` for all dependencies

## Backend Deployment (Railway)

### 1. Create Railway Project
- [ ] Sign up at [Railway.app](https://railway.app)
- [ ] Create new project from GitHub repo
- [ ] Select `write-aid-mcp` repository

### 2. Configure Environment Variables
Add these in Railway dashboard → Variables:

**Required:**
- [ ] `FINCHAT_MCP_URL` = `https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse`
- [ ] `PORT` = `5001`
- [ ] `DEBUG` = `False`

**Optional:**
- [ ] `FINCHAT_BASE_URL`
- [ ] `FINCHAT_API_TOKEN`
- [ ] `CORS_ORIGINS` (add after frontend deployed)

### 3. Deploy and Test
- [ ] Wait for deployment to complete
- [ ] Copy your Railway URL (e.g., `https://your-app.railway.app`)
- [ ] Test: `curl https://your-app.railway.app/health`
- [ ] Test: `curl https://your-app.railway.app/api/config`
- [ ] Verify MCP is enabled in config response

### 4. Note Your URLs
```
Backend URL: _______________________________________________
```

## Frontend Deployment (Vercel)

### 1. Update Backend URL
- [ ] Edit `ai_checker_config.js`
- [ ] Replace `https://your-railway-backend.railway.app` with your actual Railway URL
- [ ] Commit and push changes:
  ```bash
  git add ai_checker_config.js
  git commit -m "Configure production backend URL"
  git push origin main
  ```

### 2. Create Vercel Project
- [ ] Sign up at [Vercel.com](https://vercel.com)
- [ ] Import `write-aid-mcp` from GitHub
- [ ] Framework: **Other** (static site)
- [ ] Build settings: leave default
- [ ] Deploy

### 3. Test Frontend
- [ ] Visit your Vercel URL (e.g., `https://your-app.vercel.app`)
- [ ] Check connection status shows "✅ MCP Connected"
- [ ] Paste test text and click GO
- [ ] Verify analysis completes (takes ~10 minutes)

### 4. Note Your URLs
```
Frontend URL: _______________________________________________
```

## Post-Deployment Configuration

### Update CORS (if needed)
If you see CORS errors:
- [ ] Go to Railway → Variables
- [ ] Add `CORS_ORIGINS` = `https://your-app.vercel.app`
- [ ] Redeploy Railway

### Verify Integration
- [ ] Frontend can reach backend
- [ ] MCP connection works
- [ ] Analysis completes successfully
- [ ] No errors in browser console
- [ ] No errors in Railway logs

## Testing Checklist

### Health Check
- [ ] Backend: `curl https://YOUR-RAILWAY-URL/health`
  - Should return `{"status": "ok", ...}`

### Config Check
- [ ] Backend: `curl https://YOUR-RAILWAY-URL/api/config`
  - Should show `"mcp_enabled": true`

### Frontend Check
- [ ] Visit frontend URL
- [ ] See "✅ MCP Connected" status
- [ ] No console errors

### Full Integration Test
- [ ] Paste test text: "Voters who are panicked about rising health care costs..."
- [ ] Click GO button
- [ ] Wait ~10 minutes
- [ ] See analysis results appear
- [ ] Results show AI percentage and suggestions

## Troubleshooting

### Backend Issues
- [ ] Check Railway logs for errors
- [ ] Verify environment variables are set
- [ ] Test health endpoint
- [ ] Check Python version (should be 3.11+)

### Frontend Issues
- [ ] Check browser console for errors
- [ ] Verify backend URL in config
- [ ] Check network tab for failed requests
- [ ] Verify CORS is configured

### MCP Issues
- [ ] Verify FINCHAT_MCP_URL is correct
- [ ] Check backend logs for MCP connection
- [ ] Test MCP endpoint: `curl -X POST https://YOUR-RAILWAY-URL/api/mcp/analyze ...`

## Optional Enhancements

### Custom Domains
- [ ] Add custom domain to Vercel
- [ ] Add custom domain to Railway
- [ ] Update frontend config with new backend domain
- [ ] Update CORS_ORIGINS with new frontend domain

### Monitoring
- [ ] Set up Railway alerts
- [ ] Set up Vercel monitoring
- [ ] Add error tracking (Sentry, etc.)

### Security
- [ ] Review environment variables
- [ ] Ensure no secrets in code
- [ ] Verify DEBUG=False in production
- [ ] Configure CORS for specific domains only

## Maintenance

### Updating Backend
```bash
git add backend_server.py
git commit -m "Update backend"
git push origin main
```
Railway will auto-deploy.

### Updating Frontend
```bash
git add ai_checker.html ai_checker.js ai_checker_config.js
git commit -m "Update frontend"
git push origin main
```
Vercel will auto-deploy.

## Documentation
- [ ] Update README with live URLs
- [ ] Document any custom configuration
- [ ] Add usage instructions for end users

## Success Criteria
✅ Backend deployed and healthy  
✅ Frontend deployed and accessible  
✅ MCP connection working  
✅ Full analysis workflow functional  
✅ No errors in production  
✅ Documentation updated  

---

**Deployment Date:** _______________  
**Deployed By:** _______________  
**Backend URL:** _______________  
**Frontend URL:** _______________  

---

## Quick Reference

### Railway Commands
```bash
# View logs
railway logs

# Open dashboard
railway open
```

### Vercel Commands
```bash
# View logs
vercel logs

# Open dashboard
vercel --prod
```

### Testing Endpoints
```bash
# Health check
curl https://YOUR-RAILWAY-URL/health

# Config check
curl https://YOUR-RAILWAY-URL/api/config

# MCP analyze (full test)
curl -X POST https://YOUR-RAILWAY-URL/api/mcp/analyze \
  -H "Content-Type: application/json" \
  -d '{"paragraph":"Test text here","purpose":"Testing"}'
```

