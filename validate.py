import os
from dotenv import load_dotenv

def main():
    print("Loading .env...")
    load_dotenv()
    
    anthropic = os.getenv("ANTHROPIC_API_KEY")
    openai = os.getenv("OPENAI_API_KEY")
    tavily = os.getenv("TAVILY_API_KEY")
    
    if not (anthropic or openai):
        print("Error: Neither ANTHROPIC_API_KEY nor OPENAI_API_KEY is set in .env")
        return
        
    if not tavily:
        print("Error: TAVILY_API_KEY is not set in .env")
        return
        
    print("OK: API Keys present.")
    
    # Test stock_tool
    print("\nTesting stock_tool('AAPL')...")
    try:
        from fin_agent.tools.stock_tool import stock_tool
        stock_res = stock_tool.invoke({"ticker": "AAPL"})
        print(f"Result (first 200 chars):\n{stock_res[:200]}...")
    except Exception as e:
        print(f"Error in stock_tool: {e}")
        return
        
    # Test news_tool
    print("\nTesting news_tool('AAPL')...")
    try:
        from fin_agent.tools.news_tool import news_tool
        news_res = news_tool.invoke({"ticker": "AAPL"})
        print(f"Result (first 200 chars):\n{news_res[:200]}...")
    except Exception as e:
        print(f"Error in news_tool: {e}")
        return
        
    print("\nOK: All validations passed. You can now run main.py!")

if __name__ == "__main__":
    main()
