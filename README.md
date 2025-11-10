# Write Aid MCP - AI Checker

An intelligent text analysis tool with MCP (Model Context Protocol) integration for detecting AI-generated content.

## 🚀 Features

- **Frontend UI**: Clean, modern interface for text analysis
- **Backend API**: Flask-based server with multiple endpoints
- **MCP Integration**: Support for Model Context Protocol clients
- **Finchat API**: Optional integration with Finchat AI services
- **Local Analysis**: Heuristic-based fallback when API is unavailable
- **Real-time Analysis**: Instant feedback on text authenticity

## 📋 Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Git (for development)

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MikeVenge/write-aid-mcp.git
   cd write-aid-mcp
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure (Optional)**:
   - Edit `ai_checker_config.js` for frontend settings
   - Set environment variables for Finchat API (see below)

## 🎯 Quick Start

### Option 1: Run with Backend (Recommended)

```bash
./start_with_backend.sh
```

This will:
- Start the backend server on port 5001
- Start the frontend server on port 8000
- Open the app in your browser

### Option 2: Run Backend and Frontend Separately

**Terminal 1 - Backend**:
```bash
python3 backend_server.py
```

**Terminal 2 - Frontend**:
```bash
python3 -m http.server 8000
```

**Browser**:
```
http://localhost:8000/ai_checker.html
```

## 🔐 Finchat API Configuration (Optional)

To use the Finchat API integration, set these environment variables:

```bash
export FINCHAT_BASE_URL="https://your-finchat-instance.com"
export FINCHAT_API_TOKEN="your_jwt_token_here"
export FINCHAT_COT_SLUG="ai-detector"
export FINCHAT_MODEL="gemini-2.5-flash"
```

See `QUICK_SETUP.md` for detailed configuration.

## 📁 Project Structure

```
write-aid-mcp/
├── ai_checker.html          # Main frontend interface
├── ai_checker.js            # Frontend JavaScript logic
├── ai_checker.css           # Styling
├── ai_checker_config.js     # Frontend configuration
├── backend_server.py        # Flask backend server
├── mcp_*.py                 # MCP client implementations
├── requirements.txt         # Python dependencies
├── start_with_backend.sh    # Startup script
└── docs/                    # Documentation files
```

## 🧪 Testing

Run the test suite:

```bash
python3 test_ai_detector.py
```

## 📚 Documentation

- **[RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md)** - Detailed running instructions
- **[BACKEND_SETUP.md](BACKEND_SETUP.md)** - Backend configuration guide
- **[QUICK_SETUP.md](QUICK_SETUP.md)** - Quick reference guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[MCP_INTEGRATION_GUIDE.md](MCP_INTEGRATION_GUIDE.md)** - MCP protocol details

## 🔍 How It Works

1. **User Input**: Paste text into the web interface
2. **Analysis**: Text is analyzed by:
   - Finchat API (if configured)
   - Local heuristic algorithms (fallback)
3. **Results**: Display confidence score and detailed analysis
4. **Feedback**: Visual indicators for AI vs. human-written content

## 🛠️ API Endpoints

### Backend Server (Port 5001)

- `GET /health` - Server health check
- `POST /analyze` - Analyze text for AI content
- `POST /mcp/analyze` - MCP-compatible analysis endpoint

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

**Mike Venge**
- GitHub: [@MikeVenge](https://github.com/MikeVenge)
- Repository: [write-aid-mcp](https://github.com/MikeVenge/write-aid-mcp)

## 🐛 Issues

Found a bug? Please open an issue on [GitHub Issues](https://github.com/MikeVenge/write-aid-mcp/issues)

## ⭐ Support

If you find this project helpful, please give it a star on GitHub!

---

**Version**: 1.0.0  
**Last Updated**: November 10, 2025

