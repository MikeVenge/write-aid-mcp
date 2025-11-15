#!/usr/bin/env python3
"""
Backend server for AI Checker with MCP support.
Handles MCP analysis requests with job-based async processing.
"""

import os
import asyncio
import uuid
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Optional
import traceback

# Import MCP client
from mcp_client_fastmcp import FinChatMCPClient

app = Flask(__name__)

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins)

# Job storage (in production, use Redis or a database)
jobs: Dict[str, Dict] = {}

# MCP client configuration
MCP_URL = os.getenv('FINCHAT_MCP_URL', '')


def get_mcp_client() -> Optional[FinChatMCPClient]:
    """Get MCP client instance."""
    if not MCP_URL:
        return None
    return FinChatMCPClient(url=MCP_URL)


def run_async_task(coro):
    """Run async coroutine in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def process_mcp_analysis(job_id: str, text: str, purpose: str):
    """Process MCP analysis in background thread."""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 10
        
        client = get_mcp_client()
        if not client:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error'] = 'MCP not configured'
            return
        
        jobs[job_id]['progress'] = 20
        
        # Run async MCP call
        result = run_async_task(client.call_tool("ai_detector", {
            "text": text,
            "purpose": purpose
        }))
        
        jobs[job_id]['progress'] = 90
        
        # Extract result content
        if hasattr(result, 'content'):
            content_parts = []
            for item in result.content:
                if hasattr(item, 'type') and item.type == 'text':
                    content_parts.append(item.text)
                elif hasattr(item, 'text'):
                    content_parts.append(item.text)
                else:
                    content_parts.append(str(item))
            
            analysis_text = '\n'.join(content_parts)
        else:
            analysis_text = str(result)
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['result'] = analysis_text
        jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error processing job {job_id}: {error_msg}")
        traceback.print_exc()
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = error_msg
        jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'mcp_configured': bool(MCP_URL),
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/config', methods=['GET'])
def config():
    """Get configuration status."""
    mcp_enabled = bool(MCP_URL)
    mcp_session_id = None
    mcp_url = None
    
    if MCP_URL:
        # Extract session ID from URL
        # Format: https://finchat-api.adgo.dev/cot-mcp/{session_id}/sse
        try:
            parts = MCP_URL.split('/cot-mcp/')
            if len(parts) > 1:
                session_part = parts[1].split('/')[0]
                mcp_session_id = session_part
            mcp_url = MCP_URL
        except:
            pass
    
    return jsonify({
        'mcp_enabled': mcp_enabled,
        'mcp_session_id': mcp_session_id,
        'mcp_url': mcp_url if mcp_enabled else None,
        'configured': mcp_enabled
    })


@app.route('/api/mcp/analyze', methods=['POST'])
def mcp_analyze():
    """Start MCP analysis job."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text') or data.get('paragraph') or data.get('sentence', '')
        purpose = data.get('purpose', 'AI detection for content analysis')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Check if MCP is configured
        if not MCP_URL:
            return jsonify({
                'error': 'MCP not configured. Set FINCHAT_MCP_URL environment variable.'
            }), 500
        
        # Create job
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            'status': 'pending',
            'progress': 0,
            'created_at': datetime.utcnow().isoformat(),
            'text': text[:100] + '...' if len(text) > 100 else text,  # Store preview
            'purpose': purpose
        }
        
        # Start background processing
        thread = threading.Thread(
            target=process_mcp_analysis,
            args=(job_id, text, purpose),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'pending',
            'message': 'Analysis job started'
        }), 202
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error starting analysis: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500


@app.route('/api/mcp/status/<job_id>', methods=['GET'])
def mcp_status(job_id: str):
    """Get MCP analysis job status."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': job.get('progress', 0)
    }
    
    if job['status'] == 'completed':
        response['result'] = job.get('result', '')
        response['completed_at'] = job.get('completed_at')
    elif job['status'] == 'failed':
        response['error'] = job.get('error', 'Unknown error')
        response['completed_at'] = job.get('completed_at')
    
    return jsonify(response)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("="*60)
    print("AI Checker Backend Server")
    print("="*60)
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"MCP Configured: {bool(MCP_URL)}")
    if MCP_URL:
        print(f"MCP URL: {MCP_URL}")
    print("="*60)
    print()
    
    app.run(host='0.0.0.0', port=port, debug=debug)

