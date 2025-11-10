# How to Fix Common Messages

## Message: "Finchat not configured - please update ai_checker_config.js..."

### What it means:
The app detected that your finchat configuration still has placeholder values, so it's using local analysis instead of connecting to finchat.

### How to fix it:

**Option 1: Use the Config Button (Easiest)**
1. Click the **⚙️ Config** button in the top right (next to the status)
2. Fill in the form:
   - **Base URL**: Your finchat instance URL (e.g., `https://finchat.example.com`)
   - **API Token**: Your JWT token
   - **CoT Slug**: `ai-detector` (or your CoT slug)
   - **Model**: `gemini-2.5-flash` (default)
3. Click **"Save Configuration"**
4. The page will automatically refresh and finchat will be connected

**Option 2: Edit the Config File**
1. Open `ai_checker_config.js` in a text editor
2. Update these two lines:
   ```javascript
   BASE_URL: 'https://your-actual-finchat-url.com',  // Your real URL
   API_TOKEN: 'your_actual_jwt_token',               // Your real token
   ```
3. Save the file
4. Refresh the browser page

### After fixing:
- Check the browser console (F12 → Console)
- You should see: `✓ Finchat client initialized successfully`
- When you click GO, it should say "Analyzing sentence 1/X..." instead of "Using local analysis"

---

## Message: "Text is too short"

### What it means:
You entered less than 10 characters of text.

### How to fix it:
Enter more text (at least 10 characters) before clicking GO.

---

## Message: "Error: Failed to create session" or "CoT execution failed"

### What it means:
The app can connect to finchat, but the API call failed. Possible causes:
- Invalid API token
- Wrong Base URL
- Network/CORS issues
- CoT slug doesn't exist

### How to fix it:
1. Verify your **Base URL** is correct
2. Verify your **API Token** is valid (not expired)
3. Check browser console (F12) for detailed error messages
4. Verify the **CoT Slug** matches your finchat CoT exactly
5. Check if there are CORS errors - you may need a backend proxy

---

## Message: "Timeout: CoT execution took longer than X seconds"

### What it means:
The finchat CoT took too long to respond (default: 5 minutes).

### How to fix it:
- The text might be too long - try shorter text
- Check if finchat server is responsive
- Increase timeout in config if needed

---

## Quick Diagnostic Steps

1. **Open browser console** (F12 → Console tab)
2. **Look for these messages**:
   - ✅ `✓ Finchat client initialized successfully` = Working!
   - ⚠️ `⚠ Finchat not configured` = Needs configuration
   - ✗ `✗ Finchat client initialization failed` = Config error

3. **Check the status bar**:
   - "Waiting for input..." = Ready
   - "Using local analysis..." = Finchat not configured
   - "Analyzing sentence 1/X..." = Finchat is working!

4. **Test the connection**:
   - Click ⚙️ Config button
   - Enter your finchat credentials
   - Save and refresh
   - Try analyzing text again

---

## Still having issues?

1. **Check browser console** for detailed error messages
2. **Verify your finchat credentials** are correct
3. **Make sure the CoT slug** matches your finchat CoT exactly
4. **Check for CORS errors** - you may need to enable CORS on your finchat server



