#!/bin/bash
# Start the backend server with MCP configuration

# Set the MCP URL
export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"

# Optional: Set model if you want to override the default
# export FINCHAT_MODEL="gemini-2.5-flash"

echo "=========================================="
echo "Starting AI Checker Backend with MCP"
echo "=========================================="
echo "MCP URL: $FINCHAT_MCP_URL"
echo ""
echo "Backend will be available at:"
echo "  http://localhost:5001"
echo ""
echo "Frontend can be opened by:"
echo "  open ai_checker.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start the backend server
python3 backend_server.py

