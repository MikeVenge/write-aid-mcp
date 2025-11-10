# How to Run AI Checker Outside of Cursor

The AI Checker is a web application that can be run in any modern web browser. Here are several ways to run it:

## Option 1: Open HTML File Directly (Simplest)

1. Navigate to the folder containing the files:
   ```bash
   cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai"
   ```

2. Open `ai_checker.html` in your web browser:
   - **macOS**: Right-click → Open With → Browser (Safari, Chrome, Firefox, etc.)
   - **Or** Double-click the file (will open in your default browser)
   - **Or** Drag the file into an open browser window

**Note**: This method may have CORS (Cross-Origin Resource Sharing) issues when connecting to finchat API. If you see CORS errors in the browser console, use Option 2 or 3.

## Option 2: Using Python's Built-in Web Server (Recommended)

This method serves the files through a local web server, which helps avoid some CORS issues:

1. Open Terminal

2. Navigate to the directory:
   ```bash
   cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai"
   ```

3. Start a local web server:

   **Python 3:**
   ```bash
   python3 -m http.server 8000
   ```

   **Python 2 (if Python 3 not available):**
   ```bash
   python -m SimpleHTTPServer 8000
   ```

4. Open your browser and go to:
   ```
   http://localhost:8000/ai_checker.html
   ```

5. To stop the server, press `Ctrl+C` in the terminal

## Option 3: Using Node.js http-server

If you have Node.js installed:

1. Install http-server globally (one-time setup):
   ```bash
   npm install -g http-server
   ```

2. Navigate to the directory:
   ```bash
   cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai"
   ```

3. Start the server:
   ```bash
   http-server -p 8000
   ```

4. Open your browser:
   ```
   http://localhost:8000/ai_checker.html
   ```

## Option 4: Using a Desktop Web Server App

You can also use GUI applications like:
- **MAMP** (macOS/Windows)
- **XAMPP** (macOS/Windows/Linux)
- **VS Code Live Server** extension (if using VS Code)

## Configuration Before Running

Before running, make sure to configure your finchat API credentials:

1. Open `ai_checker_config.js` in a text editor
2. Update these values:
   ```javascript
   const FINCHAT_CONFIG = {
       BASE_URL: 'https://your-finchat-instance.com',
       API_TOKEN: 'your_jwt_token_here',
       // ... other settings
   };
   ```

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console when trying to connect to finchat:

**Solution 1**: Use a backend proxy (see `README_AI_CHECKER.md` for example)

**Solution 2**: Configure CORS headers on your finchat server to allow your domain

**Solution 3**: Use the local fallback mode (the app will automatically fall back to local heuristic analysis if finchat API is unavailable)

### API Connection Issues

If the finchat API connection fails:
- The app will automatically fall back to local heuristic-based analysis
- Check your API credentials in `ai_checker_config.js`
- Verify your finchat instance is accessible
- Check the browser console for detailed error messages

### File Path Issues

If you're having trouble with file paths:
- Make sure all files are in the same directory:
  - `ai_checker.html`
  - `ai_checker.css`
  - `ai_checker.js`
  - `ai_checker_config.js`
- Use a web server (Options 2-4) rather than opening the file directly

## Quick Start Script

You can create a simple startup script:

**macOS/Linux** (`start_server.sh`):
```bash
#!/bin/bash
cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai"
python3 -m http.server 8000 &
echo "Server started at http://localhost:8000/ai_checker.html"
open http://localhost:8000/ai_checker.html
```

**Windows** (`start_server.bat`):
```batch
@echo off
cd "C:\Users\stevekim\Library\Mobile Documents\com~apple~CloudDocs\cursorai"
python -m http.server 8000
start http://localhost:8000/ai_checker.html
```

Make the script executable (macOS/Linux):
```bash
chmod +x start_server.sh
```

Then just run:
```bash
./start_server.sh
```

## Testing the App

1. Open the app in your browser
2. Paste some sample text into the "Text to Evaluate" panel
3. Click the "GO" button
4. Wait for the analysis to complete
5. Check the "Evaluation" panel for results

The app will work even without finchat configured - it will use the local heuristic analysis as a fallback.
