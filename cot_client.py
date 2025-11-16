#!/usr/bin/env python3
"""
FinChat COT API Client
Handles calling COT prompts via REST API instead of MCP.
"""

import os
import time
import requests
from typing import Dict, Optional, Any
import traceback


class FinChatCOTClient:
    """Client for calling FinChat COT prompts via REST API."""
    
    def __init__(self, base_url: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize the COT client.
        
        Args:
            base_url: FinChat API base URL (defaults to FINCHAT_BASE_URL env var)
            api_token: API bearer token (defaults to FINCHAT_API_TOKEN env var)
        """
        self.base_url = base_url or os.getenv('FINCHAT_BASE_URL', '').rstrip('/')
        self.api_token = api_token or os.getenv('FINCHAT_API_TOKEN', '')
        
        if not self.base_url:
            raise ValueError("FINCHAT_BASE_URL must be set")
        if not self.api_token:
            raise ValueError("FINCHAT_API_TOKEN must be set")
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
    
    def create_session(self, client_id: Optional[str] = None, data_source: str = 'alpha_vantage') -> Dict[str, Any]:
        """
        Create a new session for COT execution.
        
        Args:
            client_id: Optional unique client identifier
            data_source: Data source ('alpha_vantage' or 'edgar')
            
        Returns:
            Session object with 'id' field
        """
        url = f"{self.base_url}/api/v1/sessions/"
        payload = {
            'data_source': data_source
        }
        if client_id:
            payload['client_id'] = client_id
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
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
        
        response = requests.post(url, json=payload, headers=self.headers)
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
        
        response = requests.get(url, params=params, headers=self.headers)
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
        
        response = requests.get(url, headers=self.headers)
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

