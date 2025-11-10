# Quick Reference: Finchat API Connection

## Minimum Required (2 items)

1. **FINCHAT_BASE_URL** - Your finchat instance URL
   ```
   Example: https://finchat.yourcompany.com
   ```

2. **FINCHAT_API_TOKEN** - Your JWT token
   ```
   Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

## Optional (2 items)

3. **FINCHAT_COT_SLUG** - CoT identifier (default: `ai-detector`)
   ```
   Example: ai-detector
   ```

4. **FINCHAT_MODEL** - AI model (default: `gemini-2.5-flash`)
   ```
   Example: gemini-2.5-flash
   ```

## Quick Setup

```bash
# Set environment variables
export FINCHAT_BASE_URL="https://your-finchat-instance.com"
export FINCHAT_API_TOKEN="your_jwt_token_here"
export FINCHAT_COT_SLUG="ai-detector"
export FINCHAT_MODEL="gemini-2.5-flash"

# Start backend
python3 backend_server.py
```

## Verify It Works

```bash
curl http://localhost:5000/health
```

Should show: `"finchat_configured": true`

---

See `FINCHAT_API_REQUIREMENTS.md` for detailed information.


