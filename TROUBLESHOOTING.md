# Troubleshooting: Finchat CoT Not Accessing

## Issue: App Not Accessing Finchat CoT

### Step 1: Check Browser Console

Open the browser console (F12 → Console tab) and look for:
- ✅ `✓ Finchat client initialized successfully` - Client is working
- ⚠️ `⚠ Finchat not configured - placeholder values detected` - Config needs updating
- ✗ `✗ Finchat client initialization failed` - Error in configuration

### Step 2: Update Configuration

Edit `ai_checker_config.js` and update these values:

```javascript
const FINCHAT_CONFIG = {
    BASE_URL: 'https://your-actual-finchat-url.com',  // ← Change this!
    API_TOKEN: 'your_actual_jwt_token',                 // ← Change this!
    COT_SLUG: 'ai-detector',                           // ← Verify this matches your CoT
    // ... rest stays the same
};
```

### Step 3: Verify Configuration

After updating, **refresh the browser page** (F5 or Cmd+R). Check console again:
- Should see: `✓ Finchat client initialized successfully`
- Should see your Base URL and CoT Slug listed

### Step 4: Test the Connection

1. Enter some text in the app
2. Click "GO"
3. Check the status bar:
   - Should say "Found X sentence(s). Analyzing..."
   - Should progress: "Analyzing sentence 1/X..."
   - Should NOT say "Using local analysis"

### Common Issues

#### Issue: "Finchat not configured - placeholder values detected"
**Solution**: Update `BASE_URL` and `API_TOKEN` in `ai_checker_config.js`

#### Issue: "FINCHAT_CONFIG not found"
**Solution**: Make sure `ai_checker_config.js` is in the same directory and loads before `ai_checker.js`

#### Issue: "CoT execution failed"
**Possible causes**:
- CoT slug doesn't match (check `COT_SLUG` in config)
- CoT parameters don't match (should accept `$sentence` and `$paragraph`)
- API token is invalid
- Base URL is incorrect

#### Issue: CORS errors in console
**Solution**: Your finchat server needs to allow CORS from your domain, or use a backend proxy

### Step 5: Verify CoT Parameters

Your finchat CoT "AI Detector" should accept:
- `$sentence` - Individual sentence
- `$paragraph` - Full paragraph context

The app will try these parameter combinations:
1. `$sentence` + `$paragraph` (primary)
2. `$text` + `$context` (fallback)
3. `$input` + `$full_text` (fallback)
4. `$text` only (ultimate fallback)

### Debug Checklist

- [ ] Config file has real BASE_URL (not placeholder)
- [ ] Config file has real API_TOKEN (not placeholder)
- [ ] Browser console shows "✓ Finchat client initialized successfully"
- [ ] CoT slug matches your finchat CoT exactly
- [ ] CoT accepts `$sentence` and `$paragraph` parameters
- [ ] No CORS errors in browser console
- [ ] Network tab shows API calls to finchat (if CORS allows)

### Quick Test

Open browser console and type:
```javascript
console.log(FINCHAT_CONFIG);
```

You should see your configuration object. Check:
- `BASE_URL` should NOT be `'https://your-finchat-instance.com'`
- `API_TOKEN` should NOT be `'your_jwt_token_here'`

If they're still placeholders, update the config file and refresh.

