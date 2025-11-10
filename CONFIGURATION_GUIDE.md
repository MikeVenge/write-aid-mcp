# Configuration Guide: Connecting to Finchat CoT "AI Detector"

## Step 1: Update Configuration File

Edit `ai_checker_config.js` and update these values:

```javascript
const FINCHAT_CONFIG = {
    BASE_URL: 'https://your-actual-finchat-instance.com',  // Your finchat URL
    API_TOKEN: 'your_actual_jwt_token',                    // Your API token
    COT_SLUG: 'ai-detector',                               // Your CoT slug (see below)
    // ... other settings
};
```

## Step 2: Find Your CoT Slug

The CoT slug is the identifier for your "AI Detector" CoT in finchat. It might be:

- `ai-detector` (lowercase with dash)
- `AI-Detector` (with capital letters)
- `ai_detector` (with underscore)
- Or check your finchat CoT settings for the exact slug

**How to find it:**
1. Log into your finchat instance
2. Go to CoT management/settings
3. Find "AI Detector" CoT
4. Check its slug/identifier

## Step 3: Check CoT Parameters

The "AI Detector" CoT should accept a text parameter. Common parameter names:
- `$text`
- `$input`
- `$content`
- `$input_text`

The app will try multiple parameter names automatically, but you can verify in your CoT settings.

## Step 4: Test the Connection

1. Start the server:
   ```bash
   ./start_server.sh
   ```

2. Open: `http://localhost:8000/ai_checker.html`

3. Enter some text and click "GO"

4. Check the browser console (F12 → Console) for any errors

## Troubleshooting

### "Failed to create session"
- Check your `BASE_URL` is correct
- Verify the URL is accessible
- Ensure no trailing slash at the end of the URL

### "CoT execution failed"
- Verify your `COT_SLUG` matches exactly (case-sensitive)
- Check your API token is valid
- Look at the browser console for detailed error messages

### CORS Errors
- Your finchat server needs to allow CORS from your domain
- Or use a backend proxy (see `README_AI_CHECKER.md`)

### CoT Not Found
- Double-check the slug spelling
- Ensure the CoT is not hidden (`hidden=False` in finchat settings)
- Try the exact slug from finchat (copy-paste to avoid typos)

## Example Configuration

```javascript
const FINCHAT_CONFIG = {
    BASE_URL: 'https://finchat.example.com',
    API_TOKEN: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    COT_SLUG: 'ai-detector',
    ANALYSIS_MODEL: 'gemini-2.5-flash',
    USE_WEB_SEARCH: true,
    POLL_INTERVAL: 5000,
    MAX_POLL_ATTEMPTS: 60,
    USE_L2M2: false,
    L2M2_API_URL: 'http://l2m2-production'
};
```

## Security Note

⚠️ **Important**: The API token is stored in the JavaScript file, which means it's visible to anyone who views the page source. For production use:

1. Use a backend proxy to keep tokens secure
2. Implement authentication
3. Use environment variables with a build tool

See `README_AI_CHECKER.md` for backend proxy examples.
