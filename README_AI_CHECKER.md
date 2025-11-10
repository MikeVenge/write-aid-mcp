# Write Aid AI Checker

A web application that evaluates text to determine if it was written by AI or a human, powered by finchat CoT (Chain of Thought) API.

## Features

- Clean, modern UI matching the design specifications
- **finchat Integration**: Uses finchat CoT API for AI-powered analysis
- **Local Fallback**: Heuristic-based analysis when finchat is unavailable
- **Real-time Status Updates**: Shows progress during analysis
- **Copy/Paste Functionality**: Easy text input and result copying
- **Responsive Design**: Works on different screen sizes

## Setup

### 1. Configuration

Edit `ai_checker_config.js` to set your finchat credentials:

```javascript
const FINCHAT_CONFIG = {
    BASE_URL: 'https://your-finchat-instance.com',
    API_TOKEN: 'your_jwt_token_here',
    COT_SLUG: 'ai-text-detection',  // Or use an existing CoT slug
    ANALYSIS_MODEL: 'gemini-2.5-flash',
    USE_WEB_SEARCH: true,
    // ... other settings
};
```

### 2. Using Environment Variables (Optional)

You can also set environment variables before serving the files:

```bash
export FINCHAT_BASE_URL="https://your-finchat-instance.com"
export FINCHAT_API_TOKEN="your_jwt_token_here"
export FINCHAT_COT_SLUG="ai-text-detection"
export FINCHAT_MODEL="gemini-2.5-flash"
```

**Note**: Browser-based JavaScript cannot directly access environment variables. For production use:
- Use a backend proxy to handle API calls securely
- Or use a build tool that injects environment variables at build time

### 3. CORS Considerations

Since this is a client-side web app making API calls, you may encounter CORS (Cross-Origin Resource Sharing) issues. Solutions:

#### Option A: Enable CORS on finchat server
Configure your finchat instance to allow requests from your web app's domain.

#### Option B: Use a Backend Proxy (Recommended for Production)
Create a simple backend that proxies requests to finchat:

```python
# Example: proxy_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

FINCHAT_BASE_URL = "https://your-finchat-instance.com"
API_TOKEN = "your_jwt_token_here"

@app.route('/api/session', methods=['POST'])
def create_session():
    response = requests.post(
        f"{FINCHAT_BASE_URL}/api/v1/session/",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={}
    )
    return jsonify(response.json()), response.status_code

# ... other proxy endpoints
```

### 4. Using l2m2 Directly

If you have direct access to l2m2, you can use it instead of the finchat API:

```javascript
const FINCHAT_CONFIG = {
    USE_L2M2: true,
    L2M2_API_URL: 'http://l2m2-production',
    ANALYSIS_MODEL: 'gemini-2.5-flash',
    // ...
};
```

## Usage

1. Open `ai_checker.html` in a web browser
2. Paste or type text into the "Text to Evaluate" panel
3. Click the "GO" button
4. Wait for the analysis to complete
5. View results in the "Evaluation" panel
6. Click "Copy" to copy results to clipboard

## How It Works

### With finchat CoT

1. Creates a finchat session
2. Executes a CoT prompt with the text to analyze
3. Polls for results until analysis completes
4. Displays formatted results

### Without finchat (Fallback)

Uses heuristic-based analysis:
- Sentence length variance
- Word repetition patterns
- Transitional phrase usage
- Punctuation variety
- Paragraph breaks
- Sentence complexity

## Creating a Custom CoT in finchat

To use a custom CoT for AI detection, create a CoT in finchat with:

**Slug**: `ai-text-detection` (or update `COT_SLUG` in config)

**Prompts**:
```
Analyze the following text: $text

Determine if it was written by AI or a human. Provide:
1. Verdict (AI-generated or Human-written)
2. Confidence level (0-100%)
3. Key indicators
4. Specific evidence
5. Likelihood percentages
```

**Parameters**:
- `$text` - The text to analyze

## Troubleshooting

### "Finchat error. Using local analysis..."
- Check your API credentials in `ai_checker_config.js`
- Verify the finchat base URL is correct
- Check CORS settings if accessing from a browser
- Ensure your API token is valid

### CORS Errors
- Use a backend proxy (see Option B above)
- Or enable CORS on the finchat server

### "Timeout" Errors
- Increase `MAX_POLL_ATTEMPTS` in config
- Check network connectivity
- Verify finchat instance is responsive

## File Structure

```
ai_checker.html          # Main HTML file
ai_checker.css           # Styling
ai_checker.js            # Main application logic
ai_checker_config.js     # Configuration
README_AI_CHECKER.md     # This file
```

## License

See your project's license file.
