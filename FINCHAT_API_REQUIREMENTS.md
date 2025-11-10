# Information Needed to Link to Finchat API

## Required Information (4 pieces)

### 1. **FINCHAT_BASE_URL** (Required)
The base URL of your finchat instance.

**Example:**
```
https://finchat.yourcompany.com
https://your-instance.finchat.io
```

**How to find it:**
- Check your finchat instance URL in your browser
- Look in your finchat account settings
- Ask your finchat administrator

**⚠️ Important:** 
- Include `https://` or `http://`
- Do NOT include trailing slash (`/`)
- Must be accessible from where you're running the backend server

---

### 2. **FINCHAT_API_TOKEN** (Required)
Your JWT authentication token for finchat API.

**Example:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**How to get it:**
1. Log into your finchat instance
2. Go to API settings or Developer settings
3. Generate or copy your API token
4. It's usually a long string starting with `eyJ...` (JWT format)

**⚠️ Security:**
- Keep this secret! Never commit it to git
- Store it as an environment variable, not in code
- The backend server uses this, not the frontend

---

### 3. **FINCHAT_COT_SLUG** (Optional, but recommended)
The slug/identifier of your "AI Detector" CoT in finchat.

**Default:** `ai-detector`

**Common formats:**
- `ai-detector` (lowercase with dash)
- `AI-Detector` (with capital letters)
- `ai_detector` (with underscore)
- `ai-detector-v2` (with version)

**How to find it:**
1. Log into finchat
2. Go to CoT management/settings
3. Find your "AI Detector" CoT
4. Check its slug/identifier field
5. Copy it exactly (case-sensitive!)

**⚠️ Important:**
- Must match exactly (case-sensitive)
- If wrong, you'll get "CoT not found" errors

---

### 4. **FINCHAT_MODEL** (Optional)
The AI model to use for analysis.

**Default:** `gemini-2.5-flash`

**Common options:**
- `gemini-2.5-flash`
- `gemini-2.0-flash-exp`
- `gpt-4`
- `claude-3-opus`

**How to find it:**
- Check your finchat instance's available models
- Look in finchat settings or model list
- Use the model identifier exactly as shown

---

## How to Configure

### Option 1: Environment Variables (Recommended)

Set these before running `backend_server.py`:

```bash
export FINCHAT_BASE_URL="https://your-finchat-instance.com"
export FINCHAT_API_TOKEN="your_jwt_token_here"
export FINCHAT_COT_SLUG="ai-detector"
export FINCHAT_MODEL="gemini-2.5-flash"
```

Then run:
```bash
python3 backend_server.py
```

### Option 2: Create `.env` File

Create a `.env` file in the same directory:

```bash
FINCHAT_BASE_URL=https://your-finchat-instance.com
FINCHAT_API_TOKEN=your_jwt_token_here
FINCHAT_COT_SLUG=ai-detector
FINCHAT_MODEL=gemini-2.5-flash
```

Then install `python-dotenv`:
```bash
pip install python-dotenv
```

And update `backend_server.py` to load it:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Finchat API Endpoints Used

The backend makes these calls to finchat:

### 1. Create Session
```
POST {FINCHAT_BASE_URL}/api/v1/session/
Headers:
  Authorization: Bearer {FINCHAT_API_TOKEN}
  Content-Type: application/json
Body: {}
```

**Response:**
```json
{
  "uid": "session-uuid-here"
}
```

### 2. Execute CoT
```
POST {FINCHAT_BASE_URL}/api/v1/chat/
Headers:
  Authorization: Bearer {FINCHAT_API_TOKEN}
  Content-Type: application/json
Body: {
  "session": "session-uuid",
  "message": "/cot {COT_SLUG} $sentence={sentence} $paragraph={paragraph}",
  "analysis_model": "{FINCHAT_MODEL}",
  "use_web_search": true
}
```

**Response:**
```json
{
  "uid": "chat-uuid-here"
}
```

### 3. Get Chat Result
```
GET {FINCHAT_BASE_URL}/api/v1/chat/{chat_uid}/
Headers:
  Authorization: Bearer {FINCHAT_API_TOKEN}
```

**Response:**
```json
{
  "children": [
    {
      "intent": "complete",
      "message": "Analysis result here...",
      "metadata": {...}
    }
  ]
}
```

---

## CoT Parameter Requirements

Your finchat CoT should accept one of these parameter combinations:

**Preferred:**
- `$sentence` - Individual sentence to analyze
- `$paragraph` - Full paragraph context

**Fallback options (tried automatically):**
- `$text` + `$context`
- `$input` + `$full_text`
- `$text` (sentence only)

The backend tries all combinations automatically, so your CoT only needs to support one of them.

---

## Verification Checklist

Before running, verify:

- [ ] `FINCHAT_BASE_URL` is correct and accessible
- [ ] `FINCHAT_API_TOKEN` is valid and not expired
- [ ] `FINCHAT_COT_SLUG` matches your CoT exactly (case-sensitive)
- [ ] `FINCHAT_MODEL` is available in your finchat instance
- [ ] Backend server can reach finchat URL (no firewall blocking)
- [ ] CoT accepts the expected parameters (`$sentence`, `$paragraph`, etc.)

---

## Test Connection

After setting environment variables, test the backend:

```bash
# Start backend
python3 backend_server.py

# In another terminal, check health
curl http://localhost:5000/health
```

Should return:
```json
{
  "status": "ok",
  "finchat_configured": true,
  "timestamp": "2024-..."
}
```

If `finchat_configured: false`, check your environment variables.

---

## Troubleshooting

### "Failed to create session"
- ✅ Check `FINCHAT_BASE_URL` is correct
- ✅ Verify URL is accessible (try in browser)
- ✅ Check `FINCHAT_API_TOKEN` is valid
- ✅ Ensure no trailing slash in BASE_URL

### "CoT execution failed"
- ✅ Verify `FINCHAT_COT_SLUG` matches exactly (case-sensitive)
- ✅ Check CoT exists and is not hidden
- ✅ Verify CoT accepts the parameters being sent

### "Backend server not available"
- ✅ Make sure `backend_server.py` is running
- ✅ Check it's running on port 5000
- ✅ Verify frontend config has correct `BACKEND_URL`

### CORS Errors
- ✅ Backend handles CORS automatically
- ✅ If still seeing errors, check backend is running
- ✅ Verify frontend is calling backend, not finchat directly


