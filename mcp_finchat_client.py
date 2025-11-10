#!/usr/bin/env python3
"""
FinChat MCP Client for AI Checker
Connects to FinChat via Model Context Protocol (MCP) over SSE
Based on: https://github.com/MikeVenge/mcp-finchat
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from mcp import ClientSession
from mcp.client.sse import sse_client
import httpx
from contextlib import AsyncExitStack


class FinChatMCPClient:
    """
    MCP client for FinChat API
    Handles connection, tool discovery, and AI detection via MCP protocol
    """
    
    def __init__(self, mcp_url: str):
        """
        Initialize MCP client with SSE endpoint URL
        
        Args:
            mcp_url: Full MCP SSE endpoint URL (e.g., https://finchat-api.adgo.dev/cot-mcp/ID/sse)
        """
        self.mcp_url = mcp_url
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._connected = False
        self._read_stream = None
        self._write_stream = None
        
    async def connect(self):
        """Establish connection to MCP server via SSE"""
        if self._connected:
            return
            
        try:
            print(f"Connecting to MCP server: {self.mcp_url}")
            
            # Create SSE client connection with timeout
            connection_task = asyncio.create_task(
                self.exit_stack.enter_async_context(sse_client(self.mcp_url))
            )
            
            # Wait with timeout
            self._read_stream, self._write_stream = await asyncio.wait_for(
                connection_task, timeout=10.0
            )
            
            # Create MCP session
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self._read_stream, self._write_stream)
            )
            
            # Initialize the session with timeout
            init_task = asyncio.create_task(self.session.initialize())
            await asyncio.wait_for(init_task, timeout=10.0)
            
            self._connected = True
            print("✓ Connected to MCP server")
            
        except asyncio.TimeoutError:
            print(f"✗ Connection timeout - MCP server did not respond within 10 seconds")
            raise
        except Exception as e:
            print(f"✗ Failed to connect to MCP server: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def disconnect(self):
        """Close MCP connection"""
        if self.exit_stack:
            await self.exit_stack.aclose()
            self._connected = False
            self.session = None
            print("✓ Disconnected from MCP server")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from the MCP server
        
        Returns:
            List of tool definitions with names, descriptions, and schemas
        """
        await self.connect()
        
        if not self.session:
            print("✗ No active MCP session")
            return []
        
        try:
            # Use MCP session to list tools
            result = await self.session.list_tools()
            tools = result.tools if hasattr(result, 'tools') else []
            print(f"✓ Found {len(tools)} tools")
            
            # Convert to dict format
            tools_list = []
            for tool in tools:
                tool_dict = {
                    'name': tool.name,
                    'description': tool.description if hasattr(tool, 'description') else '',
                    'inputSchema': tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                }
                tools_list.append(tool_dict)
            
            return tools_list
                    
        except Exception as e:
            print(f"✗ Error listing tools: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific tool on the MCP server
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of tool arguments
            
        Returns:
            Tool execution result
        """
        await self.connect()
        
        if not self.session:
            return {"error": "No active MCP session"}
        
        try:
            # Use MCP session to call tool
            result = await self.session.call_tool(tool_name, arguments=arguments)
            print(f"✓ Tool '{tool_name}' executed successfully")
            
            # Extract content from result
            if hasattr(result, 'content'):
                content_list = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        content_list.append(content.text)
                    elif hasattr(content, 'data'):
                        content_list.append(content.data)
                return {
                    "success": True,
                    "content": content_list,
                    "raw": str(result)
                }
            
            return {"success": True, "result": str(result)}
                    
        except Exception as e:
            print(f"✗ Error calling tool '{tool_name}': {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all available resources from the MCP server
        
        Returns:
            List of available resources
        """
        await self.connect()
        
        if not self.session:
            return []
        
        try:
            result = await self.session.list_resources()
            resources = result.resources if hasattr(result, 'resources') else []
            print(f"✓ Found {len(resources)} resources")
            
            # Convert to dict format
            resources_list = []
            for resource in resources:
                resource_dict = {
                    'uri': resource.uri if hasattr(resource, 'uri') else '',
                    'name': resource.name if hasattr(resource, 'name') else '',
                    'description': resource.description if hasattr(resource, 'description') else ''
                }
                resources_list.append(resource_dict)
            
            return resources_list
                    
        except Exception as e:
            print(f"✗ Error listing resources: {e}")
            return []
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a specific resource from the MCP server
        
        Args:
            uri: Resource URI to read
            
        Returns:
            Resource contents
        """
        await self.connect()
        
        if not self.session:
            return {"error": "No active MCP session"}
        
        try:
            result = await self.session.read_resource(uri)
            
            if hasattr(result, 'contents'):
                contents = []
                for content in result.contents:
                    if hasattr(content, 'text'):
                        contents.append(content.text)
                    elif hasattr(content, 'blob'):
                        contents.append(content.blob)
                return {"success": True, "contents": contents}
            
            return {"success": True, "result": str(result)}
                    
        except Exception as e:
            print(f"✗ Error reading resource '{uri}': {e}")
            return {"error": str(e)}
    
    async def analyze_text(self, sentence: str, paragraph: str = "") -> Dict[str, Any]:
        """
        Analyze text for AI-generated content using MCP tools
        
        Args:
            sentence: The specific sentence to analyze
            paragraph: Full paragraph context (optional)
            
        Returns:
            Analysis result with AI detection information
        """
        await self.connect()
        
        # First, discover available tools
        tools = await self.list_tools()
        
        if not tools:
            return {
                "error": "No tools available on MCP server",
                "fallback": True
            }
        
        # Look for AI detection tool
        # Common names: "ai-detector", "detect_ai", "analyze_text", "ai_detection"
        ai_tool = None
        for tool in tools:
            tool_name = tool.get('name', '').lower()
            if any(keyword in tool_name for keyword in ['ai', 'detect', 'analyze']):
                ai_tool = tool
                break
        
        if not ai_tool:
            # Use the first available tool as fallback
            ai_tool = tools[0] if tools else None
        
        if not ai_tool:
            return {
                "error": "No suitable AI detection tool found",
                "available_tools": [t.get('name') for t in tools],
                "fallback": True
            }
        
        tool_name = ai_tool['name']
        print(f"Using tool: {tool_name}")
        
        # Prepare arguments based on tool schema
        # Try different parameter combinations
        arguments_variations = [
            {"sentence": sentence, "paragraph": paragraph},
            {"text": sentence, "context": paragraph},
            {"input": sentence, "full_text": paragraph},
            {"text": sentence},
            {"content": sentence, "context": paragraph},
        ]
        
        # Try each variation
        for arguments in arguments_variations:
            try:
                result = await self.call_tool(tool_name, arguments)
                
                if "error" not in result or not result.get("error"):
                    return {
                        "success": True,
                        "tool": tool_name,
                        "result": result,
                        "arguments_used": arguments
                    }
            except Exception as e:
                continue
        
        # If all variations failed, return error
        return {
            "error": "All parameter combinations failed",
            "tool": tool_name,
            "fallback": True
        }


async def test_mcp_connection(mcp_url: str):
    """
    Test MCP connection and print available tools
    
    Args:
        mcp_url: MCP SSE endpoint URL
    """
    print("=" * 60)
    print("Testing FinChat MCP Connection")
    print("=" * 60)
    print(f"MCP URL: {mcp_url}")
    print()
    
    client = FinChatMCPClient(mcp_url)
    
    try:
        # Test connection
        await client.connect()
        print()
        
        # List tools
        print("Available Tools:")
        print("-" * 60)
        tools = await client.list_tools()
        if tools:
            for tool in tools:
                print(f"  • {tool.get('name', 'Unknown')}")
                if 'description' in tool:
                    print(f"    {tool['description']}")
                if 'inputSchema' in tool:
                    schema = tool['inputSchema']
                    if 'properties' in schema:
                        props = schema['properties'].keys()
                        print(f"    Parameters: {', '.join(props)}")
                print()
        else:
            print("  No tools found")
        print()
        
        # List resources
        print("Available Resources:")
        print("-" * 60)
        resources = await client.list_resources()
        if resources:
            for resource in resources:
                print(f"  • {resource.get('uri', 'Unknown')}")
                if 'name' in resource:
                    print(f"    {resource['name']}")
                print()
        else:
            print("  No resources found")
        
        # Test AI detection if tools are available
        if tools:
            print()
            print("Testing AI Detection:")
            print("-" * 60)
            test_sentence = "The quick brown fox jumps over the lazy dog."
            test_paragraph = "This is a test paragraph. The quick brown fox jumps over the lazy dog. This is just a sample text."
            
            result = await client.analyze_text(test_sentence, test_paragraph)
            print("Result:")
            print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    # Test with provided MCP URL
    MCP_URL = "https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"
    
    # Run test
    asyncio.run(test_mcp_connection(MCP_URL))

