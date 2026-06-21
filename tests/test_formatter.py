import pytest
from fin_agent.output.formatter import format_report

def test_format_report_contains_ticker():
    report = format_report("TSLA", "20231024_1000", "Analysis here", "Strategy here")
    assert "TSLA" in report
    assert "TSLA — Research Report" in report

def test_format_report_contains_sections():
    report = format_report("AMZN", "20231024_1000", "My Analyst Text", "My Strategy Text")
    assert "## Market Analysis" in report
    assert "## Trading Recommendation" in report
    assert "My Analyst Text" in report
    assert "My Strategy Text" in report

def test_format_report_contains_disclaimer():
    report = format_report("GOOG", "20231024_1000", "A", "B")
    disclaimer = "This report is AI-generated for informational purposes only. Not financial advice. Always apply your own risk management."
    assert disclaimer in report
