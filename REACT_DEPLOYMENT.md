# React Frontend Deployment Guide

The frontend has been converted to a React application. Follow these updated deployment instructions.

## 🎯 Quick Start

### Local Development

#### 1. Start Backend
```bash
./start_mcp_server.sh
```

#### 2. Start Frontend
```bash
cd frontend
npm install
npm start
```

The app will open at `http://localhost:3000` and automatically proxy API requests to the backend at `http://localhost:5001`.

---

## 🚀 Production Deployment

### Part 1: Deploy Backend to Railway (Same as Before)

1. Go to [Railway.app](https://railway.app) and sign in
2. Create new project from GitHub repo
3. Add environment variable:
   ```
   FINCHAT_MCP_URL=https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse
   ```
4. Wait for deployment
5. Copy your Railway URL

### Part 2: Deploy React Frontend to Vercel

#### Option A: Automatic Deployment (Recommended)

1. Go to [Vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New..." → "Project"
3. Import your `write-aid-mcp` repository
4. Configure:
   - **Framework Preset:** Create React App
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
5. Add Environment Variable:
   - **Name:** `REACT_APP_BACKEND_URL`
   - **Value:** `https://your-railway-url.railway.app`
6. Click "Deploy"

#### Option B: Manual Configuration

If the auto-detection doesn't work:

1. Update `frontend/src/services/FinChatClient.js` line 9:
   ```javascript
   : 'https://your-actual-railway-url.railway.app'
   ```
2. Commit and push
3. Vercel will auto-deploy

---

## 📋 Configuration

### Environment Variables

#### Vercel (Frontend)
```bash
REACT_APP_BACKEND_URL=https://your-railway-backend.railway.app
```

#### Railway (Backend)
```bash
FINCHAT_MCP_URL=https://finchat-api.adgo.dev/cot-mcp/YOUR_ID/sse
PORT=5001
DEBUG=False
```

### vercel.json Configuration

The root `vercel.json` is configured for React:
```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/build",
  "framework": "create-react-app"
}
```

---

## 🏗️ Project Structure

```
write-aid-mcp/
├── frontend/                 # React application
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── App.js          # Main component
│   │   ├── App.css         # Styles
│   │   ├── index.js        # Entry point
│   │   └── services/
│   │       └── FinChatClient.js  # Backend client
│   ├── package.json        # Dependencies
│   └── README.md           # Frontend docs
│
├── backend_server.py        # Flask backend
├── mcp_client_fastmcp.py   # MCP client
├── requirements.txt         # Python dependencies
├── railway.json            # Railway config
├── vercel.json             # Vercel config
└── REACT_DEPLOYMENT.md     # This file
```

---

## 🔧 Development Workflow

### 1. Local Development
```bash
# Terminal 1: Backend
./start_mcp_server.sh

# Terminal 2: Frontend
cd frontend
npm start
```

### 2. Making Changes

**Frontend Changes:**
```bash
cd frontend
# Edit src/App.js or other files
# Hot reload will update automatically
```

**Backend Changes:**
```bash
# Edit backend_server.py
# Restart: Ctrl+C then ./start_mcp_server.sh
```

### 3. Testing
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
python3 -m pytest
```

### 4. Building for Production
```bash
cd frontend
npm run build
# Creates optimized build in build/
```

---

## 🧪 Testing Deployment

### Test Backend
```bash
curl https://your-railway-url.railway.app/health
```

### Test Frontend
1. Visit `https://your-vercel-url.vercel.app`
2. Check for "✅ MCP Connected" status
3. Paste test text and click GO
4. Wait ~10 minutes for results

---

## 🐛 Troubleshooting

### Frontend Build Issues

**Error: `REACT_APP_BACKEND_URL` not defined**
- Add environment variable in Vercel settings
- Or hardcode in `src/services/FinChatClient.js`

**Error: Module not found**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Port 3000 already in use**
```bash
# Kill the process
lsof -ti:3000 | xargs kill -9
# Or use different port
PORT=3001 npm start
```

### Backend Connection Issues

**"Backend Offline"**
1. Check Railway deployment is running
2. Verify `REACT_APP_BACKEND_URL` is set correctly
3. Check CORS is enabled on backend

**CORS Errors**
Add to Railway environment variables:
```bash
CORS_ORIGINS=https://your-vercel-url.vercel.app
```

### Deployment Issues

**Vercel build fails**
- Check build logs in Vercel dashboard
- Ensure `frontend/` directory structure is correct
- Verify `package.json` has correct scripts

**Railway backend not responding**
- Check Railway logs
- Verify `FINCHAT_MCP_URL` is set
- Ensure Python dependencies are installed

---

## 📦 Differences from Static HTML Version

### What Changed

| Aspect | Old (Static HTML) | New (React) |
|--------|------------------|-------------|
| **Framework** | Vanilla JS | React 19 |
| **Build** | No build step | npm build |
| **Dev Server** | Open HTML file | `npm start` |
| **State Management** | DOM manipulation | React hooks |
| **Components** | N/A | Reusable components |
| **Hot Reload** | No | Yes |
| **TypeScript** | No | Optional |
| **Testing** | Manual | Jest/React Testing Library |

### Benefits of React Version

✅ **Component-based** - Easier to maintain and extend  
✅ **State management** - Better handling of complex state  
✅ **Hot reload** - Faster development  
✅ **Modern tooling** - Access to React ecosystem  
✅ **Better testing** - Unit and integration tests  
✅ **Code organization** - Clear separation of concerns  

### Migration Notes

The old static files (`ai_checker.html`, `ai_checker.js`, `ai_checker.css`) are kept for reference but are no longer used. All functionality has been moved to the React app.

---

## 🔄 Updating Deployments

### Update Frontend
```bash
cd frontend
# Make changes
git add .
git commit -m "Update frontend"
git push origin main
# Vercel auto-deploys
```

### Update Backend
```bash
# Make changes to backend_server.py
git add backend_server.py
git commit -m "Update backend"
git push origin main
# Railway auto-deploys
```

---

## 🎨 Customization

### Change Colors
Edit `frontend/src/App.css`:
```css
.title-write-aid {
  color: #0066cc;  /* Your brand color */
}
```

### Add Features
Edit `frontend/src/App.js` and add new components in `frontend/src/components/`.

### Change Backend URL
Update `frontend/src/services/FinChatClient.js` or set `REACT_APP_BACKEND_URL` environment variable.

---

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [Create React App](https://create-react-app.dev/)
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)

---

## ✅ Deployment Checklist

- [ ] Backend deployed to Railway
- [ ] Frontend built successfully (`npm run build`)
- [ ] Environment variables set in Vercel
- [ ] Frontend deployed to Vercel
- [ ] Backend URL configured in frontend
- [ ] Connection status shows "✅ MCP Connected"
- [ ] Test analysis completes successfully
- [ ] No errors in browser console
- [ ] No errors in Railway logs

---

**Ready to deploy?** Follow the Quick Start above or see the detailed steps in each section.

