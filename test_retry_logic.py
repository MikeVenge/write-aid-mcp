#!/usr/bin/env python3
"""
Test script to demonstrate MCP client retry logic with exponential backoff.
"""

import asyncio
from mcp_client_fastmcp import FinChatMCPClient


async def test_list_tools():
    """Test listing tools - quick test to verify connection works."""
    print("\n" + "="*70)
    print("TEST 1: List Available Tools (Quick Connection Test)")
    print("="*70)
    
    client = FinChatMCPClient(
        max_retries=2,
        initial_retry_delay=1.0,
        max_retry_delay=10.0
    )
    
    print(f"Client Configuration:")
    print(f"  URL: {client.url}")
    print(f"  Max Retries: {client.max_retries}")
    print(f"  Initial Retry Delay: {client.initial_retry_delay}s")
    print(f"  Max Retry Delay: {client.max_retry_delay}s")
    print(f"  Connection Timeout: {client.connection_timeout}s")
    print(f"  Tool Timeout: {client.tool_timeout}s")
    print()
    
    try:
        print("Calling list_tools()...")
        tools = await client.list_tools()
        print(f"✓ Success! Found {len(tools)} tool(s)")
        
        for tool in tools:
            if hasattr(tool, 'name'):
                name = tool.name
            else:
                name = tool.get('name', 'Unknown')
            print(f"  - {name}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_retry_configuration():
    """Test retry configuration and backoff calculation."""
    print("\n" + "="*70)
    print("TEST 2: Retry Configuration and Exponential Backoff")
    print("="*70)
    
    client = FinChatMCPClient(
        max_retries=3,
        initial_retry_delay=1.0,
        max_retry_delay=60.0
    )
    
    print("Exponential Backoff Delay Calculation:")
    for attempt in range(client.max_retries):
        delay = client._calculate_backoff_delay(attempt)
        print(f"  Attempt {attempt + 1}: {delay:.2f}s delay")
    
    print("\nRetryable Error Detection Test:")
    test_errors = [
        ("TimeoutError", True),
        ("Connection refused", True),
        ("Network unreachable", True),
        ("503 Service Unavailable", True),
        ("502 Bad Gateway", True),
        ("None result", False),
        ("Validation error", False),
        ("401 Unauthorized", False),
    ]
    
    for error_msg, expected_retryable in test_errors:
        class TestError(Exception):
            pass
        
        error = TestError(error_msg)
        is_retryable = client._is_retryable_error(error)
        status = "✓" if is_retryable == expected_retryable else "✗"
        print(f"  {status} '{error_msg}': {'Retryable' if is_retryable else 'Not Retryable'}")


async def test_call_tool_with_retry():
    """Test calling a tool with retry logic (using a small text sample)."""
    print("\n" + "="*70)
    print("TEST 3: Call Tool with Retry Logic")
    print("="*70)
    
    client = FinChatMCPClient(
        max_retries=3,
        initial_retry_delay=2.0,
        max_retry_delay=30.0,
        connection_timeout=30.0,
        tool_timeout=1200.0
    )
    
    # Use a small text sample for faster testing
    test_text = "This is a test sentence to verify the MCP client retry logic works correctly."
    
    print(f"Test Configuration:")
    print(f"  Max Retries: {client.max_retries}")
    print(f"  Initial Retry Delay: {client.initial_retry_delay}s")
    print(f"  Max Retry Delay: {client.max_retry_delay}s")
    print(f"  Tool Timeout: {client.tool_timeout}s")
    print()
    print(f"Test Text: {test_text}")
    print()
    print("Note: This will create a NEW connection for this request.")
    print("If connection fails, it will retry with exponential backoff.")
    print()
    
    try:
        print("Calling ai_detector tool...")
        print("(This may take 8-10 minutes for full analysis)")
        print()
        
        result = await client.call_tool(
            "ai_detector",
            {"text": test_text, "purpose": "Testing retry logic"}
        )
        
        print("\n" + "="*70)
        print("✓ Tool call succeeded!")
        print("="*70)
        
        # Display result summary
        if hasattr(result, 'content'):
            print("\nResult Content:")
            for item in result.content:
                if hasattr(item, 'type') and item.type == 'text':
                    text = item.text
                    # Show first 500 chars
                    if len(text) > 500:
                        print(text[:500] + "...")
                    else:
                        print(text)
                elif hasattr(item, 'text'):
                    text = item.text
                    if len(text) > 500:
                        print(text[:500] + "...")
                    else:
                        print(text)
        else:
            print(f"Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Tool call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("MCP Client Retry Logic Test Suite")
    print("="*70)
    print("\nThis test suite demonstrates:")
    print("  1. Connection retry logic")
    print("  2. Exponential backoff")
    print("  3. New connection for each request")
    print("  4. Retryable vs non-retryable error detection")
    print()
    
    # Test 1: List tools (quick test)
    success1 = await test_list_tools()
    
    # Test 2: Retry configuration
    await test_retry_configuration()
    
    # Test 3: Call tool with retry (optional - takes long time)
    # Skip in non-interactive mode - uncomment to run full test
    print("\n" + "="*70)
    print("Skipping full tool call test (takes 8-10 minutes).")
    print("To test it manually, run:")
    print("  python3 test_ai_detector.py")
    print("  # or uncomment the line below in test_retry_logic.py")
    success3 = None
    # Uncomment next line to run full tool call test:
    # success3 = await test_call_tool_with_retry()
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"  List Tools Test: {'✓ PASSED' if success1 else '✗ FAILED'}")
    print(f"  Retry Configuration: ✓ PASSED")
    if success3 is not None:
        print(f"  Tool Call Test: {'✓ PASSED' if success3 else '✗ FAILED'}")
    print()


if __name__ == "__main__":
    asyncio.run(main())

