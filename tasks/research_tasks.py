from crewai import Task, Crew, Process
from fin_agent.agents.analyst import get_analyst_agent
from fin_agent.agents.strategist import get_strategist_agent

def create_tasks(ticker: str, analyst, strategist):
    analysis_task = Task(
        description=(
            f"Use stock_tool and news_tool for {ticker}. Fetch the latest 15-minute OHLCV data, technical indicators, and news. "
            "Then produce a structured analysis report with the following sections:\n"
            "  1. Price Action Summary (current price, previous close, 1-day change %, trend direction)\n"
            "  2. Technical Signals (RSI, MACD crossover, price vs SMA/EMA, Bollinger Band position)\n"
            "  3. Volume Analysis (current volume, average volume, and spike status)\n"
            "  4. News Sentiment (sentiment, top headline, top headline summary)\n"
            "  5. Overall Bias (Bullish / Bearish / Neutral with one sentence justification tied to the actual data)"
        ),
        expected_output=(
            "A structured markdown report with five sections. Use only tool outputs. "
            "If any metric is unavailable, mark it as N/A — data unavailable. No speculation or invented prices."
        ),
        agent=analyst
    )

    strategy_task = Task(
        description=(
            f"Based on the analyst report for {ticker}, produce a trading recommendation in this exact format:\n\n"
            f"  ## Trading Recommendation — {ticker}\n"
            "  **Action:** BUY / SELL / HOLD\n"
            "  **Confidence:** High / Medium / Low\n"
            "  **Entry zone:** $X.XX – $X.XX\n"
            "  **Stop-loss:** $X.XX (reason)\n"
            "  **Take-profit:** $X.XX (reason)\n"
            "  **Time horizon:** Intraday / Swing (1-3 days) / Short-term (1 week)\n"
            "  **Risk warning:** [2 sentences max]"
            "\n\nUse the analysis output only. If the analyst report contains N/A values, acknowledge reduced confidence and avoid aggressive recommendations."
        ),
        expected_output="A markdown-formatted trading recommendation following the exact template above.",
        agent=strategist,
        context=[analysis_task]
    )

    return analysis_task, strategy_task

def run_crew(ticker: str) -> tuple[str, str]:
    """
    Instantiates the Crew with both agents and both tasks, runs them sequentially,
    and returns a tuple of (analyst_output, strategy_output). 
    Wraps in try/except and returns an error string tuple on failure.
    """
    try:
        analyst = get_analyst_agent()
        strategist = get_strategist_agent()
        
        analysis_task, strategy_task = create_tasks(ticker, analyst, strategist)
        
        crew = Crew(
            agents=[analyst, strategist],
            tasks=[analysis_task, strategy_task],
            process=Process.sequential,
            memory=False,
            verbose=True
        )
        
        crew.kickoff()
        
        analyst_out = analysis_task.output.raw if analysis_task.output else "No analysis output."
        strategy_out = strategy_task.output.raw if strategy_task.output else "No strategy output."
        
        return analyst_out, strategy_out
    except Exception as e:
        error_msg = f"Error running crew for {ticker}: {str(e)}"
        return error_msg, error_msg
