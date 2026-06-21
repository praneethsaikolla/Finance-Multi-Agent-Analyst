import os
import re
from tavily import TavilyClient
from crewai.tools import tool


@tool("news_tool")
def news_tool(ticker: str, company_name: str = "") -> str:
    """
    Searches for the latest news in the last 24 hours for a given ticker and returns
    a concise summary with sentiment and the top headline.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY environment variable is not set."

    try:
        client = TavilyClient(api_key=api_key)
        query = f"{ticker} {company_name} stock financial news".strip()

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            topic="news",
            days=1
        )

        results = response.get("results", [])
        if not results:
            return f"top_headline: No recent news found for {ticker}.\nrecent_news: None"

        top = results[0]
        title = top.get("title", "No Title")
        content = top.get("content", "No summary available.")
        summary = content.split(". ")[0].strip()
        if not summary.endswith("."):
            summary = (summary[:150] + "...") if len(summary) > 150 else summary

        news_summary = [
            f"top_headline: {title}",
            f"top_summary: {summary}",
            "recent_news:"
        ]

        for i, item in enumerate(results[:5], 1):
            item_title = item.get("title", "No Title")
            item_url = item.get("url", "Unknown URL")
            item_content = item.get("content", "No summary available.")
            item_snippet = item_content.split(". ")[0].strip()
            if not item_snippet.endswith("."):
                item_snippet = (item_snippet[:140] + "...") if len(item_snippet) > 140 else item_snippet
            news_summary.append(f"  {i}. {item_title} | {item_url} | {item_snippet}")

        return "\n".join(news_summary)
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"
