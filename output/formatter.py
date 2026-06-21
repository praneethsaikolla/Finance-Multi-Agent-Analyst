def format_report(ticker: str, timestamp: str, analyst_output: str, strategy_output: str) -> str:
    """
    Formats the analysis and strategy outputs into the required markdown template.
    """
    template = f"""---
# {ticker} — Research Report
**Generated:** {timestamp} IST
**Agent:** Financial Research Agent v1.0
---

## Market Analysis

{analyst_output}

---

## Trading Recommendation

{strategy_output}

---
*This report is AI-generated for informational purposes only. Not financial advice. Always apply your own risk management.*
---"""
    return template
