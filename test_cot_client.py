#!/usr/bin/env python3
"""
Test script for FinChat COT API client.
Tests the COT client functionality with ai-detector-v2.
"""

import os
import sys
from cot_client import FinChatCOTClient


def test_cot_client():
    """Test the COT client with a sample text."""
    
    # Get configuration from environment
    base_url = os.getenv('FINCHAT_BASE_URL', '')
    api_token = os.getenv('FINCHAT_API_TOKEN', '')  # Optional
    cot_slug = os.getenv('COT_SLUG', 'ai-detector-v2')
    
    # Check configuration
    if not base_url:
        print("❌ ERROR: FINCHAT_BASE_URL environment variable not set")
        print("   Set it with: export FINCHAT_BASE_URL='https://finchat-api.adgo.dev'")
        return False
    
    print("="*70)
    print("FinChat COT Client Test")
    print("="*70)
    print(f"Base URL: {base_url}")
    print(f"COT Slug: {cot_slug}")
    if api_token:
        print(f"API Token: {'*' * min(len(api_token), 20)}... (configured)")
    else:
        print("API Token: Not set (using unauthenticated requests)")
    print()
    
    # Sample test text
    test_text = "The quick brown fox jumps over the lazy dog. This is a simple test sentence to verify the COT API client is working correctly."
    test_purpose = "Testing COT API client"
    
    print(f"Test Text: {test_text}")
    print(f"Purpose: {test_purpose}")
    print()
    print("="*70)
    print("Starting COT Analysis...")
    print("="*70)
    print()
    
    try:
        # Create client
        print("1. Creating COT client...")
        client = FinChatCOTClient(
            base_url=base_url,
            api_token=api_token if api_token else None
        )
        print("   ✓ Client created")
        if api_token:
            print("   ✓ Using authenticated requests")
        else:
            print("   ✓ Using unauthenticated requests")
        print()
        
        # Define progress callback
        def progress_callback(progress: int, status: str):
            print(f"   Progress: {progress}% - {status}")
        
        # Run COT
        print("2. Running COT analysis...")
        print("   (This may take 8-10 minutes)")
        print()
        
        result = client.run_cot_complete(
            cot_slug=cot_slug,
            parameters={
                'text': test_text,
                'purpose': test_purpose
            },
            progress_callback=progress_callback
        )
        
        print()
        print("="*70)
        print("✓ Analysis Complete!")
        print("="*70)
        print()
        print(f"Session ID: {result.get('session_id')}")
        print(f"Result ID: {result.get('result_id')}")
        print()
        print("Result Content:")
        print("-" * 70)
        content = result.get('content', '')
        if content:
            # Show first 1000 characters
            if len(content) > 1000:
                print(content[:1000])
                print("...")
                print(f"[Content truncated. Full length: {len(content)} characters]")
            else:
                print(content)
        else:
            print("(No content returned)")
        print("-" * 70)
        
        return True
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print()
    success = test_cot_client()
    print()
    if success:
        print("="*70)
        print("✓ Test completed successfully!")
        print("="*70)
        sys.exit(0)
    else:
        print("="*70)
        print("✗ Test failed")
        print("="*70)
        sys.exit(1)

