#!/usr/bin/env python3
"""
FinChat COT API Client
Handles calling COT prompts via REST API instead of MCP.
"""

import os
import json
import time
import requests
import polling2
from typing import Dict, Optional, Any
import traceback


class FinChatCOTClient:
    """Client for calling FinChat COT prompts via REST API."""
    
    def __init__(self, base_url: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize the COT client.
        
        Args:
            base_url: FinChat API base URL (defaults to FINCHAT_BASE_URL env var)
            api_token: API bearer token (optional, defaults to FINCHAT_API_TOKEN env var if set)
        """
        self.base_url = base_url or os.getenv('FINCHAT_BASE_URL', '').rstrip('/')
        self.api_token = api_token or os.getenv('FINCHAT_API_TOKEN', '')
        
        if not self.base_url:
            raise ValueError("FINCHAT_BASE_URL must be set")
        
        # Build headers - only include Authorization if token is provided
        self.headers = {
            'Content-Type': 'application/json'
        }
        if self.api_token:
            self.headers['Authorization'] = f'Bearer {self.api_token}'
    
    def create_session(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new session for COT execution.
        
        Args:
            client_id: Unique client identifier (required by API, auto-generated if not provided)
            
        Returns:
            Session object with 'id' field
        """
        url = f"{self.base_url}/api/v1/sessions/"
        
        # client_id is required by the API
        if not client_id:
            import uuid
            client_id = f"client-{uuid.uuid4().hex[:12]}"
        
        payload = {
            'client_id': client_id
        }
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def upload_document(
        self, 
        session_id: str, 
        file_path: Optional[str] = None,
        file_content: Optional[bytes] = None,
        file_name: Optional[str] = None,
        consomme_id: Optional[str] = None,
        custom_properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload a document to Consomme and attach it to a FinChat session.
        
        Args:
            session_id: Session UID to attach document to
            file_path: Path to PDF file to upload (mutually exclusive with file_content)
            file_content: File content as bytes (mutually exclusive with file_path)
            file_name: Name of the file (required if using file_content)
            consomme_id: Existing Consomme document ID (if not uploading new file)
            custom_properties: Optional dict with 'title' and/or 'file_url'
            
        Returns:
            Document object with 'id', 'title', 'file_url', 'consomme_id'
        """
        url = f"{self.base_url}/api/v1/documents/"
        
        # Prepare form data
        data = {
            'session': session_id
        }
        
        files = None
        
        if file_path:
            # Upload from file path
            with open(file_path, 'rb') as f:
                files = {
                    'files': (os.path.basename(file_path), f, 'application/pdf')
                }
                if custom_properties:
                    data['custom_properties'] = json.dumps([custom_properties])
                
                # Use different headers for multipart/form-data
                headers = {}
                if self.api_token:
                    headers['Authorization'] = f'Bearer {self.api_token}'
                
                response = requests.post(url, files=files, data=data, headers=headers, timeout=60)
        elif file_content and file_name:
            # Upload from file content
            files = {
                'files': (file_name, file_content, 'application/pdf')
            }
            if custom_properties:
                data['custom_properties'] = json.dumps([custom_properties])
            
            headers = {}
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=60)
        elif consomme_id:
            # Use existing Consomme ID
            data['consomme_ids'] = [consomme_id]
            if custom_properties:
                data['custom_properties'] = [custom_properties]
            
            response = requests.post(url, json=data, headers=self.headers, timeout=60)
        else:
            raise ValueError("Either file_path, (file_content and file_name), or consomme_id must be provided")
        
        response.raise_for_status()
        result = response.json()
        # API returns a list, return first document
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result
    
    def run_cot(self, session_id: str, cot_slug: str, parameters: Dict[str, str]) -> Dict[str, Any]:
        """
        Run a COT prompt.
        
        Args:
            session_id: Session ID from create_session
            cot_slug: COT slug (e.g., 'ai-detector-v2')
            parameters: Dictionary of parameters to pass to COT
            
        Returns:
            Chat object with 'id' field (the COT chat ID)
        """
        url = f"{self.base_url}/api/v1/chats/"
        
        # Construct COT message: "cot {slug} $param1:value1 $param2:value2"
        cot_message = f"cot {cot_slug}"
        if parameters:
            param_string = ' '.join([f"${key}:{value}" for key, value in parameters.items()])
            cot_message += f" {param_string}"
        
        payload = {
            'session': session_id,
            'message': cot_message
        }
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_chats(self, session_id: str, page_size: int = 500) -> Dict[str, Any]:
        """
        Get all chats for a session.
        
        Args:
            session_id: Session ID
            page_size: Number of chats to retrieve
            
        Returns:
            Dictionary with 'results' list of chats
        """
        url = f"{self.base_url}/api/v1/chats/"
        params = {
            'session_id': session_id,
            'page_size': page_size
        }
        
        response = requests.get(url, params=params, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_result(self, result_id: str) -> Dict[str, Any]:
        """
        Get result content by result ID.
        
        Args:
            result_id: Result ID from completed chat
            
        Returns:
            Result object with 'content' field
        """
        url = f"{self.base_url}/api/v1/results/{result_id}/"
        
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def poll_for_completion(
        self, 
        session_id: str, 
        cot_chat_id: str,
        max_attempts: int = 200,
        interval_seconds: int = 5,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Poll for COT completion.
        
        Args:
            session_id: Session ID
            cot_chat_id: COT chat ID from run_cot
            max_attempts: Maximum number of polling attempts
            interval_seconds: Seconds between polling attempts
            progress_callback: Optional callback(progress, status) for progress updates
            
        Returns:
            Dictionary with 'result_id' and 'metadata'
            
        Raises:
            TimeoutError: If COT doesn't complete within max_attempts
            RuntimeError: If COT execution fails
        """
        for attempt in range(max_attempts):
            try:
                chats_data = self.get_chats(session_id)
                chats = chats_data.get('results', [])
                
                # Find the response chat (where respond_to matches cot_chat_id)
                response_chat = None
                for chat in chats:
                    if chat.get('respond_to') == cot_chat_id:
                        response_chat = chat
                        break
                
                if not response_chat:
                    # No response yet, wait and retry
                    if progress_callback:
                        progress_callback(0, 'waiting')
                    time.sleep(interval_seconds)
                    continue
                
                # Check for errors
                if response_chat.get('intent') == 'error':
                    error_msg = response_chat.get('message', 'COT execution failed')
                    raise RuntimeError(f"COT execution failed: {error_msg}")
                
                # Check if complete (has result_id)
                result_id = response_chat.get('result_id')
                if result_id:
                    metadata = response_chat.get('metadata', {})
                    if progress_callback:
                        progress_callback(100, 'completed')
                    return {
                        'response_chat_id': response_chat.get('id'),
                        'result_id': result_id,
                        'metadata': metadata
                    }
                
                # Still running - check progress
                metadata = response_chat.get('metadata', {})
                if metadata and progress_callback:
                    current_progress = metadata.get('current_progress', 0)
                    total_progress = metadata.get('total_progress', 100)
                    progress = int((current_progress / total_progress * 100)) if total_progress > 0 else 0
                    current_step = metadata.get('current_step', 'Processing...')
                    progress_callback(progress, current_step)
                
                # Wait before next poll
                time.sleep(interval_seconds)
                
            except requests.RequestException as e:
                print(f"Error polling for completion (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(interval_seconds)
                    continue
                raise
        
        raise TimeoutError(f"COT execution timed out after {max_attempts} attempts")
    
    def run_cot_complete(
        self,
        cot_slug: str,
        parameters: Dict[str, str],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Run a COT prompt and wait for completion.
        
        Args:
            cot_slug: COT slug (e.g., 'ai-detector-v2')
            parameters: Dictionary of parameters
            progress_callback: Optional callback(progress, status) for progress updates
            
        Returns:
            Dictionary with 'content', 'content_translated', 'session_id', 'result_id'
        """
        # Step 1: Create session
        session = self.create_session(client_id=f"client-{int(time.time())}")
        session_id = session['id']
        
        # Step 2: Run COT
        cot_chat = self.run_cot(session_id, cot_slug, parameters)
        cot_chat_id = cot_chat['id']
        
        # Step 3: Poll for completion
        completion = self.poll_for_completion(
            session_id,
            cot_chat_id,
            progress_callback=progress_callback
        )
        
        # Step 4: Get results
        result = self.get_result(completion['result_id'])
        
        return {
            'session_id': session_id,
            'result_id': completion['result_id'],
            'content': result.get('content', ''),
            'content_translated': result.get('content_translated', '')
        }
    
    def poll_for_completion_v2(
        self, 
        session_id: str,
        timeout_seconds: int = 1200,
        interval_seconds: int = 5,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Poll for COT v2 completion using the correct v2 results endpoint.
        Uses polling2 library for cleaner polling logic.
        
        Args:
            session_id: New session ID from v2 response
            timeout_seconds: Maximum time to wait in seconds (default 1200 = 20 minutes)
            interval_seconds: Seconds between polling attempts (default 5)
            progress_callback: Optional callback(progress, status) for progress updates
            
        Returns:
            Dictionary with 'content' from results
            
        Raises:
            TimeoutError: If COT doesn't complete within timeout
            RuntimeError: If COT execution fails
        """
        # Use the correct v2 results endpoint
        url = f"{self.base_url}/api/v2/sessions/{session_id}/results/"
        
        start_time = time.time()
        attempt_count = 0
        
        def fetch_results():
            """Fetch results from v2 API."""
            nonlocal attempt_count
            attempt_count += 1
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            status = data.get('status')
            
            # Calculate estimated progress based on time elapsed
            elapsed = time.time() - start_time
            # Assume most COTs take 8-12 minutes, show progress accordingly
            estimated_progress = min(int((elapsed / 600) * 90), 90)  # Max 90% until actually complete
            
            if progress_callback:
                # Transform status message for better UX with progress
                if status == 'loading':
                    progress_callback(estimated_progress, f'Processing ({attempt_count})...')
                elif status == 'idle' and len(data.get('results', [])) > 0:
                    progress_callback(100, 'Completed')
                else:
                    progress_callback(estimated_progress, f'Status: {status} ({attempt_count})')
            
            # Log polling status
            print(f"[V2 Poll {attempt_count}] Status: {status}, Results: {len(data.get('results', []))}, Elapsed: {int(elapsed)}s")
            
            return data
        
        def check_success(res):
            """Check if results are ready."""
            # Check multiple success conditions for robustness
            status = res.get("status")
            results = res.get("results", [])
            
            # Success if status is idle/done/completed AND has results
            is_complete = (
                (status in ["idle", "done", "completed", "success"]) and 
                len(results) > 0
            )
            
            # Also check for error status
            if status in ["error", "failed"]:
                error_msg = res.get("error", "Unknown error")
                raise RuntimeError(f"COT v2 execution failed: {error_msg}")
            
            return is_complete
        
        try:
            # Use polling2 library for clean polling
            data = polling2.poll(
                target=fetch_results,
                check_success=check_success,
                step=interval_seconds,
                timeout=timeout_seconds,
            )
            
            if progress_callback:
                progress_callback(100, 'completed')
            
            return {
                'content': data["results"][0].get('content', ''),
                'results': data.get('results', [])
            }
            
        except polling2.TimeoutException:
            raise TimeoutError(f"COT v2 execution timed out after {timeout_seconds} seconds ({attempt_count} attempts)")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Network timeout while polling COT v2 results")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error while polling COT v2: {str(e)}")
    
    def run_cot_v2(
        self,
        session_id: str,
        text: str,
        parameter_name: str = 'paragraph',
        additional_params: Optional[Dict[str, str]] = None,
        progress_callback: Optional[callable] = None,
        timeout_seconds: int = 1200,
        interval_seconds: int = 5
    ) -> Dict[str, Any]:
        """
        Run a COT prompt using API v2 with pre-existing session.
        Uses the correct v2 polling endpoint with polling2 library.
        
        Args:
            session_id: Pre-existing COT ID (e.g., '69055d25658abfb8d334cfd6')
            text: Text to process
            parameter_name: Parameter name to use in payload ('text' or 'paragraph', default 'paragraph')
            additional_params: Optional dict of additional parameters to include in payload (e.g., {'purpose': 'general'})
            progress_callback: Optional callback(progress, status) for progress updates
            timeout_seconds: Maximum time to wait in seconds (default 1200 = 20 minutes)
            interval_seconds: Seconds between polling attempts (default 5 seconds)
            
        Returns:
            Dictionary with 'content', 'session_id'
        """
        # Step 1: Execute COT using v2 API
        url = f"{self.base_url}/api/v2/sessions/run-cot/{session_id}/"
        
        # Payload format - build with correct parameter order
        # If additional_params provided, add them first for proper ordering
        payload = {}
        
        # Add additional parameters first (e.g., 'purpose' before 'text')
        if additional_params:
            payload.update(additional_params)
        
        # Then add the main text parameter
        # ai-detector COT expects 'text', humanize-text COT expects 'paragraph'
        payload[parameter_name] = text
        
        if progress_callback:
            progress_callback(5, 'Starting COT execution...')
        
        # Add timeout to the initial POST request
        response = requests.post(url, json=payload, headers=self.headers, timeout=60)
        response.raise_for_status()
        cot_response = response.json()
        
        # The response ID is the NEW session ID
        new_session_id = cot_response.get('id')
        
        if not new_session_id:
            raise RuntimeError(f"No session ID returned from COT execution. Response: {cot_response}")
        
        if progress_callback:
            progress_callback(10, 'COT started, polling for results...')
        
        # Step 2: Poll using the correct v2 results endpoint
        result = self.poll_for_completion_v2(
            new_session_id,
            timeout_seconds=timeout_seconds,
            interval_seconds=interval_seconds,
            progress_callback=progress_callback
        )
        
        # Results are directly in the response
        return {
            'session_id': new_session_id,
            'content': result.get('content', ''),
            'results': result.get('results', [])
        }

