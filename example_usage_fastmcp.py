#!/usr/bin/env python3
"""
Example usage of the FinChat MCP client to analyze a stock.
"""

import asyncio
import json
from mcp_client import FinChatMCPClient


async def analyze_stock(ticker: str):
    """
    Analyze a stock ahead of earnings.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
    """
    client = FinChatMCPClient()
    
    print(f"Analyzing {ticker}...")
    print("-" * 60)
    
    try:
        # Call the tool
        result = await client.call_tool(
            "stock_trade_analysis_pre_earnings",
            {"stock_ticker": ticker}
        )
        
        # Display the result
        print("\nResult:")
        
        # Handle the result object
        if hasattr(result, 'content'):
            # It's a result object with content
            for item in result.content:
                if hasattr(item, 'type') and item.type == 'text':
                    print(item.text)
                elif hasattr(item, 'text'):
                    print(item.text)
                else:
                    print(item)
        elif isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function to demonstrate usage."""
    
    # Example: Analyze IBM
    await analyze_stock("IBM")


if __name__ == "__main__":
    asyncio.run(main())

