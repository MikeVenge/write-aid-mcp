#!/usr/bin/env python3
"""
Simple MCP client to connect to and call the FinChat MCP server.
Implements connection retry logic with exponential backoff and creates a new connection for each request.
"""

import asyncio
from typing import Any, Dict, Optional
from fastmcp import Client

# Import FastMCP exceptions for better error handling
try:
    from fastmcp.exceptions import ToolError
except ImportError:
    # Fallback if ToolError is not available
    ToolError = Exception


class FinChatMCPClient:
    """Client for connecting to the FinChat MCP server with retry logic and exponential backoff."""
    
    def __init__(
        self, 
        url: str = "https://finchat-api.adgo.dev/cot-mcp/68e8b27f658abfa9795c85da/sse",
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        connection_timeout: float = 30.0,
        tool_timeout: float = 1200.0
    ):
        """
        Initialize the MCP client.
        
        Args:
            url: The MCP server URL
            max_retries: Maximum number of retry attempts (default: 3)
            initial_retry_delay: Initial delay between retries in seconds (default: 1.0)
            max_retry_delay: Maximum delay between retries in seconds (default: 60.0)
            connection_timeout: Timeout for establishing connection in seconds (default: 30.0)
            tool_timeout: Timeout for tool execution in seconds (default: 1200.0 = 20 minutes)
        """
        self.url = url
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay
        self.connection_timeout = connection_timeout
        self.tool_timeout = tool_timeout
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Args:
            error: The exception that occurred
            
        Returns:
            True if the error is retryable, False otherwise
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Retryable errors: connection issues, timeouts, network errors
        retryable_patterns = [
            'timeout',
            'connection',
            'network',
            'unreachable',
            'refused',
            'reset',
            'broken pipe',
            'connection aborted',
            'connection lost',
            'temporary failure',
            'service unavailable',
            'gateway timeout',
            'bad gateway',
            '503',
            '502',
            '504'
        ]
        
        # Non-retryable errors: validation errors, authentication errors, None results
        non_retryable_patterns = [
            'none',
            'validation',
            'invalid',
            'authentication',
            'authorization',
            '401',
            '403',
            '400',
            'malformed',
            'syntax error'
        ]
        
        # Check for non-retryable patterns first
        for pattern in non_retryable_patterns:
            if pattern in error_str:
                return False
        
        # Check for retryable patterns
        for pattern in retryable_patterns:
            if pattern in error_str:
                return True
        
        # Default: retry connection-related exceptions
        retryable_types = [
            'TimeoutError',
            'ConnectionError',
            'OSError',
            'IOError',
            'asyncio.TimeoutError'
        ]
        
        return error_type in retryable_types
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay for retry attempt.
        
        Args:
            attempt: The current retry attempt (0-indexed)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff: initial_delay * 2^attempt
        delay = self.initial_retry_delay * (2 ** attempt)
        # Cap at max_retry_delay
        return min(delay, self.max_retry_delay)
    
    def _create_client(self) -> Client:
        """
        Create a new Client instance for each request.
        This ensures a fresh connection for each request.
        
        Returns:
            A new Client instance
        """
        return Client(self.url, timeout=self.tool_timeout)
    
    async def list_tools(self) -> list:
        """
        List all available tools on the MCP server.
        Creates a new connection for each request.
        
        Returns:
            List of available tools with their schemas
        """
        client = self._create_client()
        async with client:
            return await client.list_tools()
    
    async def call_tool(self, tool_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Call a specific tool on the MCP server with retry logic and exponential backoff.
        Creates a new connection for each request attempt.
        
        Args:
            tool_name: The name of the tool to call
            params: Dictionary of parameters to pass to the tool
        
        Returns:
            The result from the tool execution
            
        Raises:
            ValueError: If the tool execution fails after all retries or returns None
            Exception: If a non-retryable error occurs
        """
        if params is None:
            params = {}
        
        print(f"\n{'='*60}")
        print(f"Calling tool: {tool_name}")
        print(f"Parameters: {params}")
        print(f"Max retries: {self.max_retries}")
        print(f"{'='*60}\n")
        
        last_error = None
        
        # Retry loop with exponential backoff
        for attempt in range(self.max_retries + 1):  # +1 because first attempt is not a retry
            try:
                # Create a new client connection for each attempt
                client = self._create_client()
                
                if attempt > 0:
                    delay = self._calculate_backoff_delay(attempt - 1)
                    print(f"Retry attempt {attempt}/{self.max_retries} after {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                
                print(f"Attempt {attempt + 1}/{self.max_retries + 1}: Creating new connection to MCP server...")
                
                # Use connection timeout for establishing connection
                # Use asyncio.wait_for for compatibility with Python < 3.11
                async with client:
                    print("Connection established. Sending request to MCP server...")
                    result = await asyncio.wait_for(
                        client.call_tool(tool_name, params),
                        timeout=self.tool_timeout
                    )
                
                # Check if result is None (this can happen if MCP server returns null)
                if result is None:
                    error_msg = f"MCP server returned None for tool '{tool_name}'. This may indicate the tool execution failed or timed out."
                    print(f"\n{'='*60}")
                    print(f"ERROR: {error_msg}")
                    print(f"{'='*60}\n")
                    raise ValueError(error_msg)
                
                print(f"\n{'='*60}")
                print("RAW RESULT RECEIVED:")
                print(f"Type: {type(result)}")
                print(f"Result repr: {repr(result)}")
                print(f"Result str: {str(result)}")
                print(f"{'='*60}\n")
                
                # Print all attributes if it's an object
                if hasattr(result, '__dict__'):
                    print("Object attributes:")
                    for key, value in result.__dict__.items():
                        print(f"  {key}: {repr(value)[:200]}")
                    print()
                
                # Print dir() to see all available attributes/methods
                print("Available attributes/methods:")
                print([attr for attr in dir(result) if not attr.startswith('_')])
                print()
                
                # Print specific attributes we're looking for
                if hasattr(result, 'content'):
                    print(f"Has 'content' attribute: YES")
                    print(f"Content type: {type(result.content)}")
                    print(f"Content value: {repr(result.content)[:500]}")
                    
                    if hasattr(result.content, '__iter__') and not isinstance(result.content, str):
                        try:
                            content_list = list(result.content)
                            print(f"Content items ({len(content_list)} items):")
                            for i, item in enumerate(content_list):
                                print(f"\n  Item {i}:")
                                print(f"    Type: {type(item)}")
                                print(f"    Repr: {repr(item)[:200]}")
                                if hasattr(item, 'type'):
                                    print(f"    item.type: {item.type}")
                                if hasattr(item, 'text'):
                                    print(f"    item.text: {item.text[:200] if len(item.text) > 200 else item.text}")
                        except Exception as iter_error:
                            print(f"Error iterating content: {iter_error}")
                
                print(f"\n{'='*60}\n")
                
                # Success - return result
                return result
                
            except ValueError as ve:
                # ValueError (None result) is not retryable
                print(f"\n{'='*60}")
                print(f"Non-retryable error (ValueError): {ve}")
                print(f"{'='*60}\n")
                raise
                
            except asyncio.TimeoutError as te:
                last_error = te
                error_msg = f"Connection timeout after {self.connection_timeout}s"
                print(f"\n{'='*60}")
                print(f"Timeout error on attempt {attempt + 1}: {error_msg}")
                print(f"{'='*60}\n")
                
                if attempt < self.max_retries and self._is_retryable_error(te):
                    print(f"Retryable error detected. Will retry...")
                    continue
                else:
                    raise ValueError(f"Connection timeout: {error_msg}") from te
                    
            except ToolError as te:
                last_error = te
                error_msg = str(te)
                print(f"\n{'='*60}")
                print(f"FastMCP ToolError on attempt {attempt + 1}:")
                print(f"Error message: {error_msg}")
                
                # Check if this is the None result error
                if "'NoneType' object has no attribute 'to_mcp_result'" in error_msg:
                    better_msg = f"MCP server returned None/null response for tool '{tool_name}'. This typically means the tool execution failed, timed out, or returned an invalid response."
                    print(f"Detected None result error - {better_msg}")
                    print(f"{'='*60}\n")
                    raise ValueError(better_msg) from te
                
                print(f"{'='*60}\n")
                
                # Check if retryable
                if attempt < self.max_retries and self._is_retryable_error(te):
                    print(f"Retryable error detected. Will retry...")
                    continue
                else:
                    import traceback
                    traceback.print_exc()
                    raise ValueError(f"Tool execution failed: {error_msg}") from te
                    
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                error_msg = str(e)
                
                print(f"\n{'='*60}")
                print(f"ERROR in call_tool (attempt {attempt + 1}/{self.max_retries + 1}):")
                print(f"Error type: {error_type}")
                print(f"Error message: {error_msg}")
                
                # Check if this is the specific FastMCP None error
                if "'NoneType' object has no attribute 'to_mcp_result'" in error_msg:
                    error_msg = f"MCP server returned None/null response for tool '{tool_name}'. The tool may have failed or the response was malformed."
                    print(f"Detected FastMCP None result error - {error_msg}")
                    print(f"{'='*60}\n")
                    raise ValueError(error_msg) from e
                
                # Try to get any partial data from the exception
                if hasattr(e, 'args'):
                    print(f"Error args: {e.args}")
                if hasattr(e, '__dict__'):
                    print(f"Error attributes: {e.__dict__}")
                
                print(f"{'='*60}\n")
                
                # Check if retryable
                if attempt < self.max_retries and self._is_retryable_error(e):
                    print(f"Retryable error detected. Will retry...")
                    continue
                else:
                    import traceback
                    traceback.print_exc()
                    raise
        
        # All retries exhausted
        error_summary = f"Failed after {self.max_retries + 1} attempts"
        if last_error:
            error_summary += f": {type(last_error).__name__}: {str(last_error)}"
        
        print(f"\n{'='*60}")
        print(f"ERROR: {error_summary}")
        print(f"{'='*60}\n")
        
        raise ValueError(f"Tool execution failed after {self.max_retries + 1} attempts: {error_summary}") from last_error
    
    async def list_resources(self) -> list:
        """
        List all available resources on the MCP server.
        Creates a new connection for each request.
        
        Returns:
            List of available resources
        """
        client = self._create_client()
        async with client:
            return await client.list_resources()
    
    async def read_resource(self, uri: str) -> Any:
        """
        Read a specific resource from the MCP server.
        Creates a new connection for each request.
        
        Args:
            uri: The URI of the resource to read
        
        Returns:
            The resource content
        """
        client = self._create_client()
        async with client:
            return await client.read_resource(uri)
    
    async def list_prompts(self) -> list:
        """
        List all available prompts on the MCP server.
        Creates a new connection for each request.
        
        Returns:
            List of available prompts
        """
        client = self._create_client()
        async with client:
            return await client.list_prompts()
    
    async def get_prompt(self, prompt_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Get a specific prompt from the MCP server.
        Creates a new connection for each request.
        
        Args:
            prompt_name: The name of the prompt to get
            params: Dictionary of parameters for the prompt
        
        Returns:
            The prompt content
        """
        if params is None:
            params = {}
        
        client = self._create_client()
        async with client:
            return await client.get_prompt(prompt_name, params)


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

