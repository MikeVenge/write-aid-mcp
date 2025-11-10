#!/usr/bin/env python3
"""
Simplified FinChat MCP Client for AI Checker
Uses direct HTTP requests to interact with FinChat MCP endpoint
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
import httpx


class FinChatMCPSimpleClient:
    """
    Simplified MCP client for FinChat API
    Uses HTTP POST requests instead of SSE streaming
    """
    
    def __init__(self, mcp_url: str):
        """
        Initialize simple MCP client
        
        Args:
            mcp_url: MCP endpoint URL
        """
        # Extract base URL and session ID from MCP URL
        # Format: https://finchat-api.adgo.dev/cot-mcp/SESSION_ID/sse
        self.mcp_url = mcp_url.replace('/sse', '')  # Remove /sse suffix
        self.base_url = mcp_url.rsplit('/cot-mcp/', 1)[0]
        self.session_id = mcp_url.split('/cot-mcp/')[1].split('/')[0] if '/cot-mcp/' in mcp_url else None
        
        print(f"Base URL: {self.base_url}")
        print(f"Session ID: {self.session_id}")
        print(f"MCP URL: {self.mcp_url}")
        
    async def call_cot(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Call Chain of Thought (CoT) directly via FinChat API
        
        Args:
            text: Text to analyze
            context: Additional context (optional)
            
        Returns:
            Analysis result
        """
        try:
            # Try different API endpoints
            endpoints = [
                f"{self.mcp_url}",
                f"{self.mcp_url}/execute",
                f"{self.base_url}/api/v1/cot/{self.session_id}",
            ]
            
            # Prepare payload
            payload = {
                "text": text,
                "context": context,
                "sentence": text,
                "paragraph": context
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for endpoint in endpoints:
                    try:
                        print(f"Trying endpoint: {endpoint}")
                        
                        # Try POST
                        response = await client.post(
                            endpoint,
                            json=payload,
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json"
                            }
                        )
                        
                        if response.status_code in [200, 201]:
                            result = response.json()
                            print(f"✓ Success with {endpoint}")
                            return {
                                "success": True,
                                "result": result,
                                "endpoint_used": endpoint
                            }
                        else:
                            print(f"  HTTP {response.status_code}: {response.text[:200]}")
                            
                    except Exception as e:
                        print(f"  Error: {e}")
                        continue
                
                return {
                    "error": "All endpoints failed",
                    "endpoints_tried": endpoints
                }
                
        except Exception as e:
            print(f"✗ Error calling CoT: {e}")
            return {"error": str(e)}
    
    async def analyze_text_direct(self, sentence: str, paragraph: str = "") -> Dict[str, Any]:
        """
        Direct text analysis without MCP protocol overhead
        Uses the embedded session ID from the MCP URL
        
        Args:
            sentence: Sentence to analyze
            paragraph: Full paragraph context
            
        Returns:
            Analysis result
        """
        return await self.call_cot(sentence, paragraph)


async def test_simple_client(mcp_url: str):
    """Test the simplified MCP client"""
    print("=" * 60)
    print("Testing Simplified FinChat MCP Client")
    print("=" * 60)
    
    client = FinChatMCPSimpleClient(mcp_url)
    
    print("\nTesting text analysis...")
    print("-" * 60)
    
    test_sentence = "The quick brown fox jumps over the lazy dog."
    test_paragraph = "This is a test paragraph. The quick brown fox jumps over the lazy dog."
    
    result = await client.analyze_text_direct(test_sentence, test_paragraph)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    
    print("=" * 60)


if __name__ == "__main__":
    MCP_URL = "https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
    asyncio.run(test_simple_client(MCP_URL))


