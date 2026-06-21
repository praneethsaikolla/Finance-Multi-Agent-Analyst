import os
import sys
import time
import logging
import argparse
import requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from fin_agent.config.settings import (
    WATCHLIST, TIMEZONE, SCHEDULE_START_HOUR, SCHEDULE_END_HOUR,
    ANTHROPIC_API_KEY, OPENAI_API_KEY, TAVILY_API_KEY, SLACK_WEBHOOK_URL
)
from fin_agent.tasks.research_tasks import run_crew
from fin_agent.output.formatter import format_report
from fin_agent.execution.alpaca_trader import parse_and_execute_strategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "output", "reports")

def ensure_reports_dir():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def startup_checks():
    if not ANTHROPIC_API_KEY and not OPENAI_API_KEY:
        raise RuntimeError("Neither ANTHROPIC_API_KEY nor OPENAI_API_KEY is set.")
    if not TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY is missing.")
    ensure_reports_dir()

def post_to_slack(ticker: str, timestamp: str, report: str):
    if not SLACK_WEBHOOK_URL:
        return
    try:
        payload = {"text": f"*{ticker} Report — {timestamp}*\n\n{report}"}
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Failed to post {ticker} report to Slack: {e}")

def run_agent_job(tickers: list[str] = None):
    tickers_to_run = tickers if tickers else WATCHLIST
    start_time = time.time()
    n = 0
    
    for ticker in tickers_to_run:
        logging.info(f"Starting analysis for {ticker}...")
        try:
            analyst_out, strategy_out = run_crew(ticker)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            formatted_report = format_report(ticker, timestamp, analyst_out, strategy_out)
            
            # Save to file
            filepath = os.path.join(REPORTS_DIR, f"{ticker}_{timestamp}.md")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(formatted_report)
                
            logging.info(f"Saved report to {filepath}")
            
            # Execute paper trade if applicable
            trade_result = parse_and_execute_strategy(ticker, strategy_out)
            if trade_result.get("status") == "success":
                formatted_report += f"\n\n## Execution\n✅ Paper Trade Executed: {trade_result['side'].upper()} {trade_result['qty']} shares. Order ID: {trade_result['order_id']}"
            
            # Send to Slack
            post_to_slack(ticker, timestamp, formatted_report)
            n += 1
            
        except Exception as e:
            logging.error(f"Error processing {ticker}: {e}")
            
    elapsed = time.time() - start_time
    print(f"Done! Completed {n} tickers in {elapsed:.1f}s")

def get_llm_provider_name():
    if ANTHROPIC_API_KEY:
        return "Claude 3.5 Sonnet"
    if OPENAI_API_KEY:
        return "GPT-4o"
    return "Unknown"

def print_banner():
    llm = get_llm_provider_name()
    outputs = "Slack + output/reports/" if SLACK_WEBHOOK_URL else "output/reports/"
    watchlist_str = ", ".join(WATCHLIST)
    
    banner = f"""
======================================
 Financial Research Agent - Active
 Watchlist : {watchlist_str}
 Schedule  : Every 3min | Mon-Fri | {SCHEDULE_START_HOUR:02d}:00-{SCHEDULE_END_HOUR:02d}:00 {TIMEZONE}
 LLM       : {llm}
 Output    : {outputs}
======================================
"""
    print(banner)

def main():
    parser = argparse.ArgumentParser(description="Financial Research Agent")
    parser.add_argument("--run-now", action="store_true", help="Run immediately and exit")
    parser.add_argument("--ticker", type=str, help="Run for a single ticker and print to stdout")
    args = parser.parse_args()
    
    startup_checks()
    
    if args.ticker:
        # Run single ticker to stdout
        logging.getLogger().setLevel(logging.WARNING) # Suppress normal info logs
        analyst_out, strategy_out = run_crew(args.ticker)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        report = format_report(args.ticker, timestamp, analyst_out, strategy_out)
        
        # Execute paper trade if applicable
        trade_result = parse_and_execute_strategy(args.ticker, strategy_out)
        if trade_result.get("status") == "success":
            report += f"\n\n## Execution\n✅ Paper Trade Executed: {trade_result['side'].upper()} {trade_result['qty']} shares. Order ID: {trade_result['order_id']}"
            
        print(report)
        return
        
    if args.run_now:
        print_banner()
        run_agent_job()
        return
        
    print_banner()
    scheduler = BlockingScheduler(timezone=TIMEZONE)
    
    trigger = CronTrigger(
        minute='*/3',
        hour=f'{SCHEDULE_START_HOUR}-{SCHEDULE_END_HOUR}',
        day_of_week='mon-fri',
        timezone=TIMEZONE
    )
    
    scheduler.add_job(run_agent_job, trigger=trigger)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down gracefully...")

if __name__ == "__main__":
    main()
