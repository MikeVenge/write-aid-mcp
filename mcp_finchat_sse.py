#!/usr/bin/env python3
"""
FinChat MCP Client using SSE directly
"""

import asyncio
import json
from typing import Dict, Any
import httpx
from httpx_sse import aconnect_sse


class FinChatMCPSSEClient:
    """
    MCP client using httpx-sse for Server-Sent Events
    """
    
    def __init__(self, mcp_url: str):
        self.mcp_url = mcp_url
        self.base_url = mcp_url.rsplit('/cot-mcp/', 1)[0]
        self.session_id = mcp_url.split('/cot-mcp/')[1].split('/')[0] if '/cot-mcp/' in mcp_url else None
        
    async def send_mcp_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send an MCP JSON-RPC request via SSE
        
        Args:
            method: MCP method name (e.g., "tools/list", "tools/call")
            params: Method parameters
            
        Returns:
            Response from server
        """
        request_id = 1
        request_data = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with aconnect_sse(
                    client,
                    "POST",
                    self.mcp_url,
                    json=request_data,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream"
                    }
                ) as event_source:
                    print(f"✓ Connected to SSE stream")
                    
                    async for sse in event_source.aiter_sse():
                        print(f"Received event: {sse.event}")
                        print(f"Data: {sse.data[:200] if len(sse.data) > 200 else sse.data}")
                        
                        try:
                            data = json.loads(sse.data)
                            if data.get('id') == request_id:
                                return data.get('result', data)
                        except json.JSONDecodeError:
                            continue
                    
                    return {"error": "No response received"}
                    
        except Exception as e:
            print(f"✗ SSE error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        print("Requesting tools list...")
        return await self.send_mcp_request("tools/list")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        print(f"Calling tool: {tool_name}")
        return await self.send_mcp_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
    
    async def analyze_text(self, sentence: str, paragraph: str = "") -> Dict[str, Any]:
        """Analyze text using available tools"""
        # First, discover tools
        tools_result = await self.list_tools()
        print(f"Tools discovery result: {tools_result}")
        
        if "error" in tools_result:
            return tools_result
        
        # Try to find AI detection tool and call it
        tools = tools_result.get('tools', [])
        if not tools:
            return {"error": "No tools available"}
        
        # Use first available tool
        tool_name = tools[0].get('name') if tools else "analyze"
        
        return await self.call_tool(tool_name, {
            "sentence": sentence,
            "paragraph": paragraph
        })


async def test_sse_client(mcp_url: str):
    """Test SSE-based MCP client"""
    print("=" * 60)
    print("Testing FinChat MCP with SSE")
    print("=" * 60)
    print(f"URL: {mcp_url}\n")
    
    client = FinChatMCPSSEClient(mcp_url)
    
    # Test tool listing
    print("1. Listing available tools...")
    print("-" * 60)
    tools = await client.list_tools()
    print(f"Result: {json.dumps(tools, indent=2)}\n")
    
    # Test text analysis
    print("2. Testing text analysis...")
    print("-" * 60)
    result = await client.analyze_text(
        "The quick brown fox jumps over the lazy dog.",
        "This is a test paragraph."
    )
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    print("=" * 60)


if __name__ == "__main__":
    MCP_URL = "https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
    
    try:
        asyncio.run(test_sse_client(MCP_URL))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")


