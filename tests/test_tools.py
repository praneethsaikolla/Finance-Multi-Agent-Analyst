import pytest
import pandas as pd
from fin_agent.tools.stock_tool import stock_tool
from fin_agent.tools.news_tool import news_tool

def test_stock_tool_valid_ticker(monkeypatch):
    # Mock yfinance data for a valid ticker
    class MockTicker:
        def history(self, period, interval):
            dates = pd.date_range(end=pd.Timestamp.now(), periods=25, freq='15T')
            close = pd.Series([150 + i * 0.1 for i in range(25)], index=dates)
            volume = pd.Series([100000 + i * 1000 for i in range(25)], index=dates)
            df = pd.DataFrame({
                'Close': close,
                'Volume': volume
            }, index=dates)
            return df

    monkeypatch.setattr("fin_agent.tools.stock_tool.yf.Ticker", lambda ticker: MockTicker())

    result = stock_tool.run("AAPL")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "RSI" in result
    assert "MACD" in result

def test_stock_tool_invalid_ticker(monkeypatch):
    class MockTickerEmpty:
        def history(self, period, interval):
            return pd.DataFrame()

    monkeypatch.setattr("fin_agent.tools.stock_tool.yf.Ticker", lambda ticker: MockTickerEmpty())

    result = stock_tool.run("XXXXINVALID")
    assert isinstance(result, str)
    assert "Error:" in result or "No data found" in result

def test_news_tool(monkeypatch):
    # Mock the TavilyClient
    class MockClient:
        def __init__(self, api_key):
            self.api_key = api_key

        def search(self, *args, **kwargs):
            return {
                "results": [
                    {
                        "title": "Microsoft Announces New AI Features",
                        "url": "https://example.com/msft-news",
                        "content": "Microsoft is launching a new suite of AI features for Office 365. It will change everything."
                    }
                ]
            }

    monkeypatch.setattr("fin_agent.tools.news_tool.TavilyClient", MockClient)
    monkeypatch.setenv("TAVILY_API_KEY", "fake_api_key")

    result = news_tool.run("MSFT")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Microsoft Announces New AI Features" in result
    assert "Source: https://example.com/msft-news" in result
