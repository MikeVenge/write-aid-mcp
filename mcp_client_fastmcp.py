#!/usr/bin/env python3
"""
Simple MCP client to connect to and call the FinChat MCP server.
"""

import asyncio
from typing import Any, Dict, Optional
from fastmcp import Client


class FinChatMCPClient:
    """Client for connecting to the FinChat MCP server."""
    
    def __init__(self, url: str = "https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse"):
        """
        Initialize the MCP client.
        
        Args:
            url: The MCP server URL
        """
        self.url = url
        self.client = Client(url)
    
    async def list_tools(self) -> list:
        """
        List all available tools on the MCP server.
        
        Returns:
            List of available tools with their schemas
        """
        async with self.client:
            return await self.client.list_tools()
    
    async def call_tool(self, tool_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Call a specific tool on the MCP server.
        
        Args:
            tool_name: The name of the tool to call
            params: Dictionary of parameters to pass to the tool
        
        Returns:
            The result from the tool execution
        """
        if params is None:
            params = {}
        
        async with self.client:
            result = await self.client.call_tool(tool_name, params)
            return result
    
    async def list_resources(self) -> list:
        """
        List all available resources on the MCP server.
        
        Returns:
            List of available resources
        """
        async with self.client:
            return await self.client.list_resources()
    
    async def read_resource(self, uri: str) -> Any:
        """
        Read a specific resource from the MCP server.
        
        Args:
            uri: The URI of the resource to read
        
        Returns:
            The resource content
        """
        async with self.client:
            return await self.client.read_resource(uri)
    
    async def list_prompts(self) -> list:
        """
        List all available prompts on the MCP server.
        
        Returns:
            List of available prompts
        """
        async with self.client:
            return await self.client.list_prompts()
    
    async def get_prompt(self, prompt_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Get a specific prompt from the MCP server.
        
        Args:
            prompt_name: The name of the prompt to get
            params: Dictionary of parameters for the prompt
        
        Returns:
            The prompt content
        """
        if params is None:
            params = {}
        
        async with self.client:
            return await self.client.get_prompt(prompt_name, params)


# Example usage
async def main():
    """Example usage of the FinChat MCP client."""
    
    # Create client instance
    client = FinChatMCPClient()
    
    print("Connecting to FinChat MCP server...")
    print(f"URL: {client.url}\n")
    
    try:
        # List available tools
        print("=== Available Tools ===")
        tools = await client.list_tools()
        print(f"Found {len(tools)} tool(s)\n")
        for tool in tools:
            # Handle both dict and object types
            if hasattr(tool, 'name'):
                name = tool.name
                description = getattr(tool, 'description', 'No description')
                input_schema = getattr(tool, 'inputSchema', None)
            else:
                name = tool.get('name', 'Unknown')
                description = tool.get('description', 'No description')
                input_schema = tool.get('inputSchema', None)
            
            print(f"Tool: {name}")
            print(f"Description: {description}")
            
            # Display input parameters
            if input_schema:
                print("Parameters:")
                properties = input_schema.get('properties', {}) if isinstance(input_schema, dict) else getattr(input_schema, 'properties', {})
                required = input_schema.get('required', []) if isinstance(input_schema, dict) else getattr(input_schema, 'required', [])
                
                if properties:
                    for param_name, param_info in properties.items():
                        param_type = param_info.get('type', 'unknown') if isinstance(param_info, dict) else getattr(param_info, 'type', 'unknown')
                        param_desc = param_info.get('description', '') if isinstance(param_info, dict) else getattr(param_info, 'description', '')
                        is_required = " (required)" if param_name in required else " (optional)"
                        print(f"  - {param_name}: {param_type}{is_required}")
                        if param_desc:
                            print(f"    {param_desc}")
                else:
                    print("  No parameters")
            else:
                print("Parameters: No schema available")
            
            print()
        print()
        
        # List available resources
        print("=== Available Resources ===")
        try:
            resources = await client.list_resources()
            print(f"Found {len(resources)} resource(s)\n")
            for resource in resources:
                # Handle both dict and object types
                if hasattr(resource, 'uri'):
                    uri = resource.uri
                    name = getattr(resource, 'name', 'No name')
                else:
                    uri = resource.get('uri', 'Unknown')
                    name = resource.get('name', 'No name')
                print(f"- {uri}: {name}")
        except Exception as e:
            print(f"Resources not available: {e}")
        print()
        
        # List available prompts
        print("=== Available Prompts ===")
        try:
            prompts = await client.list_prompts()
            print(f"Found {len(prompts)} prompt(s)\n")
            for prompt in prompts:
                # Handle both dict and object types
                if hasattr(prompt, 'name'):
                    name = prompt.name
                    description = getattr(prompt, 'description', 'No description')
                else:
                    name = prompt.get('name', 'Unknown')
                    description = prompt.get('description', 'No description')
                print(f"- {name}: {description}")
        except Exception as e:
            print(f"Prompts not available: {e}")
        print()
        
        # Example: Call a tool (uncomment and modify when you know the tool name)
        # print("=== Calling Tool ===")
        # result = await client.call_tool("tool_name", {"param1": "value1"})
        # print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

