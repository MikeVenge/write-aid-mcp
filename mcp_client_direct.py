#!/usr/bin/env python3
"""
Direct MCP client using httpx to avoid FastMCP hanging issues.
"""

import asyncio
import httpx
import json
from typing import Any, Dict, Optional


class DirectMCPClient:
    """Direct MCP client without using FastMCP library."""
    
    def __init__(self, url: str):
        """
        Initialize the direct MCP client.
        
        Args:
            url: The MCP server SSE URL
        """
        self.url = url
        # Extract base URL (remove /sse suffix)
        self.base_url = url.rsplit('/sse', 1)[0] if '/sse' in url else url
    
    async def call_tool(self, tool_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Call a tool using direct HTTP request.
        
        Args:
            tool_name: Name of the tool to call
            params: Tool parameters
            
        Returns:
            Tool result
        """
        if params is None:
            params = {}
        
        # Try different endpoint formats
        endpoints = [
            f"{self.base_url}/tools/{tool_name}",
            f"{self.base_url}/tool/{tool_name}",
            f"{self.base_url}/call/{tool_name}",
        ]
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=10.0)) as client:
            for endpoint in endpoints:
                try:
                    print(f"Trying endpoint: {endpoint}")
                    
                    response = await client.post(
                        endpoint,
                        json=params,
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        }
                    )
                    
                    print(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"Got result: {type(result)}")
                        return result
                    elif response.status_code == 404:
                        # Try next endpoint
                        continue
                    else:
                        print(f"Error response: {response.text[:200]}")
                        
                except httpx.HTTPStatusError as e:
                    print(f"HTTP error for {endpoint}: {e}")
                    continue
                except Exception as e:
                    print(f"Error for {endpoint}: {e}")
                    continue
            
            # If all endpoints failed, raise error
            raise Exception(f"Could not find working endpoint for tool '{tool_name}'")


async def test_direct_client():
    """Test the direct client."""
    client = DirectMCPClient("https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse")
    
    text = "We are building a world class AI research lab in Tokyo."
    
    print("Testing direct MCP client...")
    print(f"Text: {text}")
    print()
    
    try:
        result = await client.call_tool("ai_detector", {
            "text": text,
            "purpose": "Testing"
        })
        
        print("Result:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct_client())

