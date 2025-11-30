# GO Button Migration to v2 API

## What Changed

The **GO button** has been migrated from the old COT API (slug-based) to the new v2 API (session-based), matching how GO2 works.

### Before
- GO button used: `run_cot_complete()` with `COT_SLUG='ai-detector-v2'`
- Called: `/api/v1/chats/` → posted `cot ai-detector-v2 $text:... $purpose:...`
- Different API pathway than GO2

### After
- GO button now uses: `run_cot_v2()` with `COT_SESSION_ID='68e8b27f658abfa9795c85da'`
- Calls: `/api/v2/sessions/run-cot/68e8b27f658abfa9795c85da/`
- **Same API pathway as GO2** (both use v2 API)

## Why This Change?

1. **Consistency**: Both GO and GO2 now use the same v2 API infrastructure
2. **Better Performance**: v2 API has improved polling and timeout handling
3. **Unified Codebase**: Easier to maintain with both buttons using same code path
4. **Fixed Timeouts**: GO button now gets all the timeout fixes from GO2

## Environment Variables

### Old Variable (Deprecated)
```bash
COT_SLUG=ai-detector-v2  # ❌ NO LONGER USED
```

### New Variables
```bash
COT_SESSION_ID=68e8b27f658abfa9795c85da        # GO button (defaults to this value)
COT_V2_SESSION_ID=6923bb68658abf729a7b8994    # GO2 button (defaults to this value)
```

## API Endpoint Change

### GO Button Endpoint
```
Old: POST /api/v1/chats/
     Body: { "session": "...", "message": "cot ai-detector-v2 $text:... $purpose:..." }

New: POST /api/v2/sessions/run-cot/68e8b27f658abfa9795c85da/
     Body: { "paragraph": "..." }
```

### GO2 Button Endpoint (Unchanged)
```
POST /api/v2/sessions/run-cot/6923bb68658abf729a7b8994/
Body: { "paragraph": "..." }
```

## Code Changes

### backend_server.py

#### 1. Updated Configuration
```python
# OLD:
COT_SLUG = os.getenv('COT_SLUG', 'ai-detector-v2')

# NEW:
COT_SESSION_ID = os.getenv('COT_SESSION_ID', '68e8b27f658abfa9795c85da')  # GO button
COT_V2_SESSION_ID = os.getenv('COT_V2_SESSION_ID', '6923bb68658abf729a7b8994')  # GO2 button
```

#### 2. Updated process_cot_analysis()
```python
# OLD:
result = client.run_cot_complete(
    cot_slug=COT_SLUG,
    parameters={
        'text': text,
        'purpose': purpose
    },
    progress_callback=callback
)

# NEW:
result = client.run_cot_v2(
    session_id=COT_SESSION_ID,
    paragraph=text,
    progress_callback=callback
)
```

#### 3. Updated Health & Config Endpoints
```python
# OLD:
return jsonify({
    'cot_slug': COT_SLUG,
    ...
})

# NEW:
return jsonify({
    'cot_session_id': COT_SESSION_ID,
    ...
})
```

## Benefits

### 1. Unified Timeout Handling
Both GO and GO2 now use the same timeout configuration:
- **20 minute timeout** (was 10 minutes for old GO)
- **5 second polling interval** (was varied before)
- **Progress estimation** during execution (0% → 90% → 100%)

### 2. Better Error Handling
- Network timeouts: 30 seconds max
- Proper error messages from API
- Multiple success condition checks

### 3. Consistent User Experience
- Both buttons show same progress indicators
- Same status message format
- Same completion behavior

### 4. Simplified Maintenance
- Single code path for both buttons
- Easier to debug and improve
- Centralized timeout and polling logic

## Testing

### Test GO Button
```bash
# Start analysis
curl -X POST http://localhost:5001/api/mcp/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Test text with at least 250 words...","purpose":"Testing GO v2 API"}'

# Response:
# {"job_id":"xxx-xxx-xxx","status":"pending","message":"Analysis job started"}

# Check status
curl http://localhost:5001/api/mcp/status/xxx-xxx-xxx

# Response:
# {"job_id":"xxx","status":"processing","progress":45,"status_message":"Processing (attempt 18)..."}
```

### Test GO2 Button
```bash
# Start analysis
curl -X POST http://localhost:5001/api/mcp/analyze-v2 \
  -H "Content-Type: application/json" \
  -d '{"text":"Test text...","purpose":"Testing"}'

# Status check same as GO button
```

### Expected Behavior
Both buttons should:
1. Show progress 0% → 90% → 100%
2. Update status every 5 seconds
3. Complete within 8-12 minutes (typical)
4. Support up to 20 minutes execution time
5. Show proper error messages if they fail

## Deployment

### Railway Environment Variables

Remove old variable (if exists):
```bash
# Delete this from Railway dashboard:
COT_SLUG
```

Add new variables (optional - have defaults):
```bash
# Only add if you want to override defaults:
COT_SESSION_ID=68e8b27f658abfa9795c85da
COT_V2_SESSION_ID=6923bb68658abf729a7b8994
```

### No Frontend Changes Needed
The frontend doesn't change - it still calls the same backend endpoints:
- GO button → `/api/mcp/analyze`
- GO2 button → `/api/mcp/analyze-v2`

Backend internally routes these to v2 API now.

## Backward Compatibility

✅ **No Breaking Changes**
- Frontend code unchanged
- API endpoints unchanged  
- Only internal routing changed
- Default values provide backward compatibility

❌ **Deprecated**
- `COT_SLUG` environment variable (no longer used)
- `run_cot_complete()` method for GO button (still exists but not used)

## Rollback Plan

If issues occur:

```bash
# Revert to previous version
git revert <commit-hash>
git push origin main

# Or restore old code:
# In backend_server.py, change process_cot_analysis() to use:
result = client.run_cot_complete(
    cot_slug='ai-detector-v2',
    parameters={'text': text, 'purpose': purpose},
    progress_callback=callback
)
```

## Monitoring

After deployment, monitor for:

1. **Success Rate**: Both buttons should complete successfully
2. **Timing**: Should complete in 8-12 minutes (typical)
3. **Errors**: Check logs for any new error patterns
4. **Progress**: Verify progress bar moves smoothly

## Files Modified

1. `backend_server.py` - Updated GO button to use v2 API
2. `RAILWAY_ENV_VARS.md` - Updated environment variable documentation
3. `GO_V2_API_MIGRATION.md` - This migration guide

---

**Status:** ✅ Ready for Deployment  
**Risk Level:** LOW - Internal routing change only  
**Impact:** GO button gets all timeout/polling improvements from GO2  
**User Impact:** Better reliability, faster error detection, visible progress

