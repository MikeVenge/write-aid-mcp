#!/bin/bash
# Start Backend Server with FinChat MCP Configuration

export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
export FINCHAT_MODEL="gemini-2.5-flash"
export FINCHAT_COT_SLUG="ai-detector"

cd "/Users/stevekim/Library/Mobile Documents/com~apple~CloudDocs/cursorai/AI Checker2"

echo "=============================================="
echo "Starting Backend with FinChat MCP"
echo "=============================================="
echo "MCP URL: $FINCHAT_MCP_URL"
echo "Model: $FINCHAT_MODEL"
echo "=============================================="

python3 backend_server.py

