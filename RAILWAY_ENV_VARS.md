# Railway Environment Variables

## Required Environment Variables

### NEW - Required for COT API

```bash
FINCHAT_BASE_URL=https://finchat-api.adgo.dev
```

### Optional

```bash
FINCHAT_API_TOKEN=your_jwt_token_here                     # Only if authentication is required
COT_SESSION_ID=68e8b27f658abfa9795c85da                   # GO button session ID (defaults to this)
COT_V2_SESSION_ID=6923bb68658abf729a7b8994                # GO2 button session ID (defaults to this)
PORT=5001                                                 # Defaults to 5001 if not set
DEBUG=False                                               # Set to True for debug mode
CORS_ORIGINS=https://your-frontend-domain.com             # Comma-separated list
```

## OLD - Remove These (No Longer Needed)

```bash
FINCHAT_MCP_URL=...  # ❌ Remove this - no longer used
```

## Complete Railway Environment Variables Setup

### Step 1: Remove Old Variables
In Railway Dashboard → Variables, delete:
- `FINCHAT_MCP_URL`

### Step 2: Add New Variables
In Railway Dashboard → Variables, add:

**Required:**
```
FINCHAT_BASE_URL = https://finchat-api.adgo.dev
```

**Optional (only if authentication is required):**
```
FINCHAT_API_TOKEN = your_jwt_token_here
```

**Recommended:**
```
COT_SESSION_ID = 68e8b27f658abfa9795c85da
COT_V2_SESSION_ID = 6923bb68658abf729a7b8994
PORT = 5001
DEBUG = False
```

**Optional (if you have a frontend):**
```
CORS_ORIGINS = https://www.writeaid.me,https://writeaid-me.vercel.app
```
Note: Use comma-separated list for multiple domains. Default is `*` (allows all origins).

## Quick Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FINCHAT_BASE_URL` | ✅ Yes | - | FinChat API base URL |
| `FINCHAT_API_TOKEN` | ❌ No | - | Bearer token (only if authentication required) |
| `COT_SESSION_ID` | ❌ No | `68e8b27f658abfa9795c85da` | GO button COT session ID (v2 API) |
| `COT_V2_SESSION_ID` | ❌ No | `6923bb68658abf729a7b8994` | GO2 button COT session ID (v2 API) |
| `PORT` | ❌ No | `5001` | Server port |
| `DEBUG` | ❌ No | `False` | Enable debug mode |
| `CORS_ORIGINS` | ❌ No | `*` | Allowed CORS origins |

## Migration Checklist

- [ ] Remove old variables from Railway (if present): `FINCHAT_MCP_URL`, `COT_SLUG`
- [ ] Add `FINCHAT_BASE_URL` to Railway variables
- [ ] Optionally add `FINCHAT_API_TOKEN` (only if authentication is required)
- [ ] Optionally add `COT_SESSION_ID=68e8b27f658abfa9795c85da` (GO button)
- [ ] Optionally add `COT_V2_SESSION_ID=6923bb68658abf729a7b8994` (GO2 button)
- [ ] Verify `PORT=5001` is set
- [ ] Set `DEBUG=False` for production
- [ ] Redeploy Railway service
- [ ] Test health endpoint: `curl https://your-railway-url.railway.app/health`
- [ ] Test config endpoint: `curl https://your-railway-url.railway.app/api/config`

## Testing After Update

```bash
# Health check
curl https://your-railway-url.railway.app/health

# Expected response:
# {
#   "status": "ok",
#   "cot_configured": true,
#   "cot_session_id": "68e8b27f658abfa9795c85da",
#   "timestamp": "..."
# }

# Config check
curl https://your-railway-url.railway.app/api/config

# Expected response:
# {
#   "cot_enabled": true,
#   "cot_session_id": "68e8b27f658abfa9795c85da",
#   "base_url": "https://finchat-api.adgo.dev",
#   "configured": true
# }
```

