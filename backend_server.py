#!/usr/bin/env python3
"""
Backend server for AI Checker with FinChat COT API support.
Handles COT analysis requests with job-based async processing.
"""

import os
import uuid
import re
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from typing import Dict, Optional
import traceback

# Import COT client
from cot_client import FinChatCOTClient

app = Flask(__name__)

# Configure CORS - allow all origins by default
cors_origins_env = os.getenv('CORS_ORIGINS', '*')
# Handle both comma-separated list and single value
if cors_origins_env == '*' or cors_origins_env.strip() == '':
    cors_origins = '*'  # Allow all origins
    print(f"CORS configured: Allowing all origins (*)")
else:
    # Split by comma and strip whitespace
    cors_origins = [origin.strip() for origin in cors_origins_env.split(',') if origin.strip()]
    print(f"CORS configured: Allowing origins: {cors_origins}")
# Configure CORS with explicit options
CORS(app, 
     origins=cors_origins,
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'])

# Job storage (in production, use Redis or a database)
jobs: Dict[str, Dict] = {}

# COT configuration
COT_SESSION_ID = os.getenv('COT_SESSION_ID', '68e8b27f658abfa9795c85da')  # GO button session ID (v2 API)
COT_V2_SESSION_ID = os.getenv('COT_V2_SESSION_ID', '6923bb68658abf729a7b8994')  # GO2 session ID (v2 API)
FINCHAT_BASE_URL = os.getenv('FINCHAT_BASE_URL', '')
FINCHAT_API_TOKEN = os.getenv('FINCHAT_API_TOKEN', '')  # Optional

# PDF file for GO button patterns
PATTERNS_PDF_PATH = os.getenv('PATTERNS_PDF_PATH', 'COMPREHENSIVE LIST OF SIGNS OF AI WRITING.pdf')


def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing or replacing special tokens that cause issues with tiktoken encoding.
    FinChat's tiktoken encoder throws errors when encountering certain special tokens like <|endoftext|>.
    
    Args:
        text: Input text that may contain problematic special tokens
        
    Returns:
        Sanitized text with special tokens removed or replaced
    """
    if not text:
        return text
    
    # List of special tokens that cause issues with tiktoken
    # These are common GPT/LLM special tokens that should be removed or replaced
    problematic_tokens = [
        '<|endoftext|>',
        '<|end_of_text|>',
        '<|fim_prefix|>',
        '<|fim_middle|>',
        '<|fim_suffix|>',
        '<|fim_pad|>',
        '<|startoftext|>',
        '<|start_of_text|>',
    ]
    
    sanitized = text
    for token in problematic_tokens:
        # Replace with empty string (remove) or replace with a space if you want to preserve spacing
        sanitized = sanitized.replace(token, ' ')
    
    # Clean up multiple spaces that might result from replacements
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    return sanitized.strip()


def get_cot_client() -> Optional[FinChatCOTClient]:
    """Get COT client instance."""
    if not FINCHAT_BASE_URL:
        return None
    try:
        # Pass token only if provided (it's optional)
        return FinChatCOTClient(
            base_url=FINCHAT_BASE_URL,
            api_token=FINCHAT_API_TOKEN if FINCHAT_API_TOKEN else None
        )
    except Exception as e:
        print(f"Error creating COT client: {e}")
        return None


def progress_callback(job_id: str):
    """Create a progress callback function for a specific job."""
    def callback(progress: int, status: str):
        if job_id in jobs:
            jobs[job_id]['progress'] = progress
            jobs[job_id]['status_message'] = status
    return callback


def process_cot_analysis(job_id: str, text: str, purpose: str, file_content: Optional[bytes] = None, file_name: Optional[str] = None):
    """Process COT analysis in background thread (GO button - using ai-detector-v2 COT directly)."""
    try:
        # Sanitize text to remove problematic special tokens (safety measure)
        text = sanitize_text(text)
        
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 5
        jobs[job_id]['status_message'] = 'Initializing...'
        
        client = get_cot_client()
        if not client:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error'] = 'COT API not configured. Set FINCHAT_BASE_URL environment variable.'
            return
        
        jobs[job_id]['progress'] = 10
        jobs[job_id]['status_message'] = 'Creating session...'
        
        # Step 1: Create a new session
        session_response = client.create_session()
        session_id = session_response.get('id')
        if not session_id:
            raise RuntimeError(f"No session ID returned. Response: {session_response}")
        
        jobs[job_id]['progress'] = 20
        jobs[job_id]['status_message'] = 'Uploading patterns document...'
        
        # Step 2: Upload patterns PDF file to Consomme
        # Always upload the COMPREHENSIVE LIST OF SIGNS OF AI WRITING.pdf file
        consomme_id = None
        try:
            # Get the absolute path to the PDF file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            pdf_path = os.path.join(script_dir, PATTERNS_PDF_PATH)
            
            if not os.path.exists(pdf_path):
                print(f"Warning: Patterns PDF file not found at {pdf_path}")
            else:
                # Upload the PDF file using file_path
                document_response = client.upload_document(
                    session_id=session_id,
                    file_path=pdf_path
                )
                consomme_id = document_response.get('consomme_id')
                if not consomme_id:
                    print(f"Warning: No consomme_id returned from document upload. Response: {document_response}")
                else:
                    print(f"Successfully uploaded patterns PDF, consomme_id: {consomme_id}")
        except Exception as e:
            print(f"Warning: Failed to upload patterns PDF: {e}")
            traceback.print_exc()
            # Continue without file if upload fails, but log the error
            consomme_id = None
        
        # Also handle user-provided file if any (for future extensibility)
        if file_content and file_name:
            try:
                print(f"Also uploading user-provided file: {file_name}")
                user_doc_response = client.upload_document(
                    session_id=session_id,
                    file_content=file_content,
                    file_name=file_name
                )
                # Note: We only use the patterns PDF consomme_id for the $patterns parameter
                # User files are attached to the session but not passed as patterns
            except Exception as e:
                print(f"Warning: Failed to upload user-provided file: {e}")
        
        jobs[job_id]['progress'] = 30
        jobs[job_id]['status_message'] = 'Starting COT analysis...'
        
        # Step 3: Call COT with ai-detector-v2 slug
        # Parameter order: $purpose (first), $patterns (second), $text (third)
        cot_slug = 'ai-detector-v2'
        parameters = {
            'purpose': 'general'
        }
        
        # Add patterns parameter second if we have a consomme_id
        if consomme_id:
            parameters['patterns'] = consomme_id
        
        # Add text parameter third
        parameters['text'] = text
        
        callback = progress_callback(job_id)
        cot_chat = client.run_cot(session_id=session_id, cot_slug=cot_slug, parameters=parameters)
        cot_chat_id = cot_chat.get('id')
        
        if not cot_chat_id:
            raise RuntimeError(f"No chat ID returned from COT execution. Response: {cot_chat}")
        
        jobs[job_id]['progress'] = 40
        jobs[job_id]['status_message'] = 'Waiting for analysis to complete...'
        
        # Step 4: Poll for completion with progress mapping (40% to 90%)
        def mapped_callback(poll_progress: int, status: str):
            # Map polling progress (0-100) to overall progress (40-90)
            mapped_progress = 40 + int(poll_progress * 0.5)
            callback(mapped_progress, status)
        
        result_data = client.poll_for_completion(
            session_id=session_id,
            cot_chat_id=cot_chat_id,
            max_attempts=200,
            interval_seconds=5,
            progress_callback=mapped_callback
        )
        
        result_id = result_data.get('result_id')
        if not result_id:
            raise RuntimeError(f"No result_id returned from polling. Response: {result_data}")
        
        jobs[job_id]['progress'] = 90
        jobs[job_id]['status_message'] = 'Retrieving results...'
        
        # Step 5: Get result content
        result = client.get_result(result_id)
        content = result.get('content', '')
        
        if not content:
            # Try to get content from metadata if available
            metadata = result_data.get('metadata', {})
            content = metadata.get('content', '') or str(result)
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['status_message'] = 'Completed'
        jobs[job_id]['result'] = content
        jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error processing job {job_id}: {error_msg}")
        traceback.print_exc()
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = error_msg
        jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()


def process_cot_v2_analysis(job_id: str, text: str, purpose: str):
    """Process COT v2 analysis in background thread (for GO2 button)."""
    try:
        # Sanitize text to remove problematic special tokens (safety measure)
        text = sanitize_text(text)
        
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 5
        jobs[job_id]['status_message'] = 'Initializing v2...'
        
        client = get_cot_client()
        if not client:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error'] = 'COT API not configured. Set FINCHAT_BASE_URL environment variable.'
            return
        
        jobs[job_id]['progress'] = 10
        jobs[job_id]['status_message'] = 'Starting v2 analysis...'
        
        # Run COT v2 with progress callback
        # Note: v2 session uses 'humanize-text' COT which expects 'paragraph' parameter
        callback = progress_callback(job_id)
        result = client.run_cot_v2(
            session_id=COT_V2_SESSION_ID,
            text=text,
            parameter_name='paragraph',  # humanize-text COT expects 'paragraph' parameter
            progress_callback=callback
        )
        
        # Extract result content (v2 returns content directly)
        content = result.get('content', '')
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['status_message'] = 'Completed'
        jobs[job_id]['result'] = content
        jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error processing v2 job {job_id}: {error_msg}")
        traceback.print_exc()
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = error_msg
        jobs[job_id]['completed_at'] = datetime.utcnow().isoformat()


@app.route('/health', methods=['GET', 'OPTIONS'])
@cross_origin()
def health():
    """Health check endpoint."""
    cot_configured = bool(FINCHAT_BASE_URL)
    
    # Check if PDF file exists (for version verification)
    pdf_exists = False
    pdf_path = None
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(script_dir, PATTERNS_PDF_PATH)
        pdf_exists = os.path.exists(pdf_path)
    except Exception:
        pass
    
    return jsonify({
        'status': 'ok',
        'cot_configured': cot_configured,
        'cot_session_id': COT_SESSION_ID if cot_configured else None,
        'pdf_file_exists': pdf_exists,
        'pdf_path': pdf_path if pdf_exists else None,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/config', methods=['GET', 'OPTIONS'])
@cross_origin()
def config():
    """Get configuration status."""
    cot_enabled = bool(FINCHAT_BASE_URL)
    
    return jsonify({
        'cot_enabled': cot_enabled,
        'cot_session_id': COT_SESSION_ID if cot_enabled else None,
        'base_url': FINCHAT_BASE_URL if cot_enabled else None,
        'configured': cot_enabled
    })


@app.route('/api/mcp/analyze', methods=['POST', 'OPTIONS'])
@cross_origin()
def mcp_analyze():
    """Start COT analysis job using ai-detector-v2 COT with file upload support."""
    try:
        # Handle both JSON and multipart/form-data
        if request.content_type and 'multipart/form-data' in request.content_type:
            text = request.form.get('text') or request.form.get('paragraph') or request.form.get('sentence', '')
            purpose = request.form.get('purpose', 'AI detection for content analysis')
            file = request.files.get('file')  # Single file upload
        else:
            data = request.get_json() or {}
            text = data.get('text') or data.get('paragraph') or data.get('sentence', '')
            purpose = data.get('purpose', 'AI detection for content analysis')
            file = None
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Sanitize text to remove problematic special tokens (e.g., <|endoftext|>)
        text = sanitize_text(text)
        
        # Check if COT API is configured
        if not FINCHAT_BASE_URL:
            return jsonify({
                'error': 'COT API not configured. Set FINCHAT_BASE_URL environment variable.'
            }), 500
        
        # Store file content if provided
        file_content = None
        file_name = None
        if file:
            file_content = file.read()
            file_name = file.filename
        
        # Create job
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            'status': 'pending',
            'progress': 0,
            'status_message': 'Queued',
            'created_at': datetime.utcnow().isoformat(),
            'text': text[:100] + '...' if len(text) > 100 else text,  # Store preview
            'purpose': purpose,
            'has_file': file is not None
        }
        
        # Start background processing
        thread = threading.Thread(
            target=process_cot_analysis,
            args=(job_id, text, purpose, file_content, file_name),
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


@app.route('/api/mcp/status/<job_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def mcp_status(job_id: str):
    """Get COT analysis job status (kept endpoint name for backward compatibility)."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': job.get('progress', 0),
        'status_message': job.get('status_message', '')
    }
    
    if job['status'] == 'completed':
        response['result'] = job.get('result', '')
        response['completed_at'] = job.get('completed_at')
    elif job['status'] == 'failed':
        response['error'] = job.get('error', 'Unknown error')
        response['completed_at'] = job.get('completed_at')
    
    return jsonify(response)


@app.route('/api/mcp/analyze-v2', methods=['POST', 'OPTIONS'])
@cross_origin()
def mcp_analyze_v2():
    """Start COT v2 analysis job (for GO2 button)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text') or data.get('paragraph') or data.get('sentence', '')
        purpose = data.get('purpose', 'AI detection for content analysis')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Sanitize text to remove problematic special tokens (e.g., <|endoftext|>)
        text = sanitize_text(text)
        
        # Check if COT API is configured
        if not FINCHAT_BASE_URL:
            return jsonify({
                'error': 'COT API not configured. Set FINCHAT_BASE_URL environment variable.'
            }), 500
        
        # Create job
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            'status': 'pending',
            'progress': 0,
            'status_message': 'Queued',
            'created_at': datetime.utcnow().isoformat(),
            'text': text[:100] + '...' if len(text) > 100 else text,  # Store preview
            'purpose': purpose,
            'type': 'v2'  # Mark as v2 job
        }
        
        # Start background processing
        thread = threading.Thread(
            target=process_cot_v2_analysis,
            args=(job_id, text, purpose),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'pending',
            'message': 'Analysis v2 job started'
        }), 202
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error starting v2 analysis: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("="*60)
    print("AI Checker Backend Server")
    print("="*60)
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"COT Configured: {bool(FINCHAT_BASE_URL)}")
    if FINCHAT_BASE_URL:
        print(f"Base URL: {FINCHAT_BASE_URL}")
    print(f"GO Session ID: {COT_SESSION_ID}")
    print(f"GO2 Session ID: {COT_V2_SESSION_ID}")
    if FINCHAT_API_TOKEN:
        print(f"API Token: {'*' * min(len(FINCHAT_API_TOKEN), 20)}... (configured)")
    else:
        print("API Token: Not set (using unauthenticated requests)")
    print("="*60)
    print()
    
    app.run(host='0.0.0.0', port=port, debug=debug)

