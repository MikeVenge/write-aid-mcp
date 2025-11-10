# Backend Server Setup

## What This Does

The `backend_server.py` is a Flask proxy server that:
- ✅ Keeps your finchat API token secure (not exposed to browser)
- ✅ Handles CORS properly
- ✅ Makes API calls to finchat on behalf of the frontend
- ✅ Provides a clean API for the frontend to use

## Architecture

```
Browser → Backend Server (Flask) → finchat API
```

Instead of:
```
Browser → finchat API (direct, insecure, CORS issues)
```

## Setup

### 1. Install Dependencies

```bash
pip install flask flask-cors requests
```

### 2. Configure Environment Variables

**Option A: Environment Variables**
```bash
export FINCHAT_BASE_URL="https://your-finchat-instance.com"
export FINCHAT_API_TOKEN="your_jwt_token_here"
export FINCHAT_COT_SLUG="ai-detector"
export FINCHAT_MODEL="gemini-2.5-flash"
```

**Option B: Create `.env` file** (recommended)
```bash
# Create .env file
cat > .env << EOF
FINCHAT_BASE_URL=https://your-finchat-instance.com
FINCHAT_API_TOKEN=your_jwt_token_here
FINCHAT_COT_SLUG=ai-detector
FINCHAT_MODEL=gemini-2.5-flash
EOF
```

Then install `python-dotenv` and load it:
```bash
pip install python-dotenv
```

### 3. Run the Backend Server

```bash
python3 backend_server.py
```

The server will start on `http://localhost:5000`

### 4. Update Frontend to Use Backend

The frontend JavaScript needs to be updated to call the backend instead of finchat directly.

## API Endpoints

- `GET /health` - Health check
- `POST /api/session` - Create finchat session
- `POST /api/chat` - Execute CoT
- `GET /api/chat/<chat_uid>` - Get chat result
- `GET /api/config` - Get configuration status



