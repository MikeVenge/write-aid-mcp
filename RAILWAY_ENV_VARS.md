# Railway Environment Variables

## Required Environment Variables

### NEW - Required for COT API

```bash
FINCHAT_BASE_URL=https://finchat-api.adgo.dev
```

### Optional

```bash
FINCHAT_API_TOKEN=your_jwt_token_here  # Only if authentication is required
COT_SLUG=ai-detector-v2                  # Defaults to 'ai-detector-v2' if not set
PORT=5001                                # Defaults to 5001 if not set
DEBUG=False                              # Set to True for debug mode
CORS_ORIGINS=https://your-frontend-domain.com  # Comma-separated list
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
COT_SLUG = ai-detector-v2
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
| `COT_SLUG` | ❌ No | `ai-detector-v2` | COT prompt slug to use |
| `PORT` | ❌ No | `5001` | Server port |
| `DEBUG` | ❌ No | `False` | Enable debug mode |
| `CORS_ORIGINS` | ❌ No | `*` | Allowed CORS origins |

## Migration Checklist

- [ ] Remove `FINCHAT_MCP_URL` from Railway variables (if present)
- [ ] Add `FINCHAT_BASE_URL` to Railway variables
- [ ] Optionally add `FINCHAT_API_TOKEN` (only if authentication is required)
- [ ] Optionally add `COT_SLUG=ai-detector-v2`
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
#   "cot_slug": "ai-detector-v2",
#   "timestamp": "..."
# }

# Config check
curl https://your-railway-url.railway.app/api/config

# Expected response:
# {
#   "cot_enabled": true,
#   "cot_slug": "ai-detector-v2",
#   "base_url": "https://finchat-api.adgo.dev",
#   "configured": true
# }
```

