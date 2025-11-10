#!/usr/bin/env python3
"""
Test the ai_detector tool
"""

import asyncio
from mcp_client_fastmcp import FinChatMCPClient


async def test_ai_detector():
    """Test the AI detector tool with sample text."""
    
    client = FinChatMCPClient()
    
    print("Testing AI Detector Tool")
    print("=" * 60)
    
    # Sample text to test
    test_text = "The quick brown fox jumps over the lazy dog. This is a simple sentence used for testing purposes."
    
    print(f"Text to analyze:\n{test_text}\n")
    print("Calling ai_detector tool (this may take ~10 minutes)...")
    print("-" * 60)
    
    try:
        # Call the tool
        result = await client.call_tool(
            "ai_detector",
            {"text": test_text, "purpose": "Testing AI detection"}
        )
        
        print("\nResult received!")
        print("=" * 60)
        
        # Display the result
        if hasattr(result, 'content'):
            print("Content:")
            for item in result.content:
                if hasattr(item, 'type') and item.type == 'text':
                    print(item.text)
                elif hasattr(item, 'text'):
                    print(item.text)
                else:
                    print(item)
        else:
            print(result)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ai_detector())


