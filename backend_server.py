#!/usr/bin/env python3
"""
Backend proxy server for AI Checker app.
Handles finchat API calls securely, keeping tokens server-side.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from datetime import datetime
import uuid
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Job storage - in production, use Redis or a database
analysis_jobs = {}

# Configuration - load from environment variables or config file
FINCHAT_BASE_URL = os.getenv('FINCHAT_BASE_URL', 'https://finchat-api.adgo.dev')
FINCHAT_API_TOKEN = os.getenv('FINCHAT_API_TOKEN', 'your_jwt_token_here')
FINCHAT_COT_SLUG = os.getenv('FINCHAT_COT_SLUG', 'ai-detector')
FINCHAT_MODEL = os.getenv('FINCHAT_MODEL', 'gemini-2.5-flash')

# MCP Configuration (optional - for MCP-based access)
FINCHAT_MCP_URL = os.getenv('FINCHAT_MCP_URL', '')
FINCHAT_MCP_SESSION_ID = None

# Extract session ID from MCP URL if provided
if FINCHAT_MCP_URL and '/cot-mcp/' in FINCHAT_MCP_URL:
    FINCHAT_MCP_SESSION_ID = FINCHAT_MCP_URL.split('/cot-mcp/')[1].split('/')[0]
    # Update base URL from MCP URL if not explicitly set
    if FINCHAT_BASE_URL == 'https://finchat-api.adgo.dev':
        FINCHAT_BASE_URL = FINCHAT_MCP_URL.rsplit('/cot-mcp/', 1)[0]
    print(f"MCP Mode: Extracted session ID: {FINCHAT_MCP_SESSION_ID}")

# Headers for finchat API
FINCHAT_HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {FINCHAT_API_TOKEN}'
}

def check_config():
    """Check if finchat is properly configured"""
    has_placeholders = (
        FINCHAT_BASE_URL == 'https://your-finchat-instance.com' or
        FINCHAT_API_TOKEN == 'your_jwt_token_here'
    )
    return not has_placeholders

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'finchat_configured': check_config(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/session', methods=['POST'])
def create_session():
    """Create a finchat session"""
    if not check_config():
        return jsonify({
            'error': 'Finchat not configured. Set FINCHAT_BASE_URL and FINCHAT_API_TOKEN environment variables.'
        }), 500
    
    try:
        response = requests.post(
            f'{FINCHAT_BASE_URL}/api/v1/session/',
            headers=FINCHAT_HEADERS,
            json={},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return jsonify({'uid': data.get('uid')})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to create session: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def execute_cot():
    """Execute a CoT (Chain of Thought) with finchat"""
    if not check_config():
        return jsonify({
            'error': 'Finchat not configured. Set FINCHAT_BASE_URL and FINCHAT_API_TOKEN environment variables.'
        }), 500
    
    try:
        data = request.json
        session_uid = data.get('session')
        sentence = data.get('sentence', '')
        paragraph = data.get('paragraph', '')
        
        if not session_uid:
            return jsonify({'error': 'Session UID is required'}), 400
        
        # Try different parameter combinations
        parameter_combinations = [
            f'/cot {FINCHAT_COT_SLUG} $sentence={sentence} $paragraph={paragraph}',
            f'/cot {FINCHAT_COT_SLUG} $text={sentence} $context={paragraph}',
            f'/cot {FINCHAT_COT_SLUG} $input={sentence} $full_text={paragraph}',
            f'/cot {FINCHAT_COT_SLUG} $text={sentence}'
        ]
        
        last_error = None
        for cot_message in parameter_combinations:
            try:
                response = requests.post(
                    f'{FINCHAT_BASE_URL}/api/v1/chat/',
                    headers=FINCHAT_HEADERS,
                    json={
                        'session': session_uid,
                        'message': cot_message,
                        'analysis_model': FINCHAT_MODEL,
                        'use_web_search': True
                    },
                    timeout=30
                )
                
                if response.ok:
                    result = response.json()
                    return jsonify({'uid': result.get('uid')})
                else:
                    last_error = f'HTTP {response.status_code}: {response.text}'
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                continue
        
        return jsonify({'error': f'All parameter combinations failed. Last error: {last_error}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Failed to execute CoT: {str(e)}'}), 500

@app.route('/api/chat/<chat_uid>', methods=['GET'])
def get_chat_result(chat_uid):
    """Get the result of a chat/CoT execution"""
    if not check_config():
        return jsonify({
            'error': 'Finchat not configured. Set FINCHAT_BASE_URL and FINCHAT_API_TOKEN environment variables.'
        }), 500
    
    try:
        response = requests.get(
            f'{FINCHAT_BASE_URL}/api/v1/chat/{chat_uid}/',
            headers=FINCHAT_HEADERS,
            timeout=10
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to get chat result: {str(e)}'}), 500

@app.route('/api/mcp/analyze', methods=['POST'])
def mcp_analyze_start():
    """
    Start an MCP analysis job and return job ID immediately.
    The analysis runs in the background.
    """
    if not FINCHAT_MCP_URL:
        return jsonify({
            'error': 'MCP not configured. Set FINCHAT_MCP_URL environment variable.'
        }), 500
    
    try:
        data = request.json
        
        # Support both formats:
        # 1. Direct text field
        # 2. Legacy sentence + paragraph format
        if 'text' in data:
            full_text = data.get('text', '')
        else:
            sentence = data.get('sentence', '')
            paragraph = data.get('paragraph', '')
            full_text = f"{sentence}\n\n{paragraph}" if paragraph else sentence
        
        purpose = data.get('purpose', 'AI detection for content analysis')
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        analysis_jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'result': None,
            'error': None,
            'created_at': datetime.now().isoformat()
        }
        
        # Start analysis in background thread
        def run_analysis():
            import asyncio
            from mcp_client_fastmcp import FinChatMCPClient
            
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Create MCP client
                client = FinChatMCPClient(FINCHAT_MCP_URL)
                
                # Call ai_detector tool
                async def analyze():
                    result = await client.call_tool(
                        "ai_detector",
                        {"text": full_text, "purpose": purpose}
                    )
                    
                    # Handle the result object
                    content_text = []
                    
                    if hasattr(result, 'content'):
                        for item in result.content:
                            if hasattr(item, 'type') and item.type == 'text':
                                content_text.append(item.text)
                            elif hasattr(item, 'text'):
                                content_text.append(item.text)
                            else:
                                content_text.append(str(item))
                        
                        return '\n'.join(content_text)
                    elif isinstance(result, dict):
                        return json.dumps(result, indent=2)
                    else:
                        return str(result)
                
                # Run with timeout
                result_text = loop.run_until_complete(
                    asyncio.wait_for(analyze(), timeout=900)
                )
                
                # Update job status
                analysis_jobs[job_id]['status'] = 'completed'
                analysis_jobs[job_id]['progress'] = 100
                analysis_jobs[job_id]['result'] = result_text
                analysis_jobs[job_id]['completed_at'] = datetime.now().isoformat()
                
                loop.close()
                
            except asyncio.TimeoutError:
                analysis_jobs[job_id]['status'] = 'failed'
                analysis_jobs[job_id]['error'] = 'Analysis timed out after 15 minutes'
            except Exception as e:
                analysis_jobs[job_id]['status'] = 'failed'
                analysis_jobs[job_id]['error'] = str(e)
                import traceback
                analysis_jobs[job_id]['traceback'] = traceback.format_exc()
        
        # Start background thread
        thread = threading.Thread(target=run_analysis, daemon=True)
        thread.start()
        
        # Return job ID immediately
        return jsonify({
            'job_id': job_id,
            'status': 'processing',
            'message': 'Analysis started. Use /api/mcp/status/<job_id> to check progress.'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': f'Failed to start analysis: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/mcp/status/<job_id>', methods=['GET'])
def mcp_analyze_status(job_id):
    """
    Get the status of an MCP analysis job.
    """
    if job_id not in analysis_jobs:
        return jsonify({
            'error': 'Job not found'
        }), 404
    
    job = analysis_jobs[job_id]
    
    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': job.get('progress', 0),
        'created_at': job['created_at']
    }
    
    if job['status'] == 'completed':
        response['result'] = job['result']
        response['completed_at'] = job.get('completed_at')
    elif job['status'] == 'failed':
        response['error'] = job.get('error')
        if 'traceback' in job:
            response['traceback'] = job['traceback']
    
    return jsonify(response)

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration status (without exposing tokens)"""
    config = {
        'configured': check_config(),
        'base_url': FINCHAT_BASE_URL if check_config() else 'not configured',
        'cot_slug': FINCHAT_COT_SLUG,
        'model': FINCHAT_MODEL,
        'mcp_enabled': FINCHAT_MCP_SESSION_ID is not None
    }
    
    if FINCHAT_MCP_SESSION_ID:
        config['mcp_session_id'] = FINCHAT_MCP_SESSION_ID
        config['mcp_url'] = FINCHAT_MCP_URL
    
    return jsonify(config)

if __name__ == '__main__':
    # Get port from environment variable (Railway/Heroku) or default to 5001
    port = int(os.getenv('PORT', 5001))
    
    print('=' * 60)
    print('AI Checker Backend Server')
    print('=' * 60)
    
    if FINCHAT_MCP_SESSION_ID:
        print('✓ MCP Mode Enabled')
        print(f'  Base URL: {FINCHAT_BASE_URL}')
        print(f'  MCP Session ID: {FINCHAT_MCP_SESSION_ID}')
        print(f'  MCP URL: {FINCHAT_MCP_URL}')
        print(f'  Model: {FINCHAT_MODEL}')
        print()
        print('  Endpoints:')
        print('    - /api/mcp/analyze - MCP-based analysis')
        print('    - /api/chat - Standard REST API (fallback)')
    elif check_config():
        print('✓ Finchat configured (REST API mode)')
        print(f'  Base URL: {FINCHAT_BASE_URL}')
        print(f'  CoT Slug: {FINCHAT_COT_SLUG}')
        print(f'  Model: {FINCHAT_MODEL}')
    else:
        print('⚠ Finchat NOT configured')
        print('  Set environment variables:')
        print('    Option 1 - MCP Mode:')
        print('      export FINCHAT_MCP_URL="https://finchat-api.adgo.dev/cot-mcp/YOUR_ID/sse"')
        print()
        print('    Option 2 - REST API Mode:')
        print('      export FINCHAT_BASE_URL="https://your-finchat-instance.com"')
        print('      export FINCHAT_API_TOKEN="your_jwt_token_here"')
    
    print('=' * 60)
    print(f'Starting server on port {port}')
    print('Press Ctrl+C to stop')
    print('=' * 60)
    
    # Use debug=False for production
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)


