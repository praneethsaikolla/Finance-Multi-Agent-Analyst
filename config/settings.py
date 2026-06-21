import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM Providers
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Tools API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Output delivery
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Agent configuration
watchlist_str = os.getenv("WATCHLIST", "AAPL,NVDA,MSFT")
WATCHLIST = [ticker.strip() for ticker in watchlist_str.split(",") if ticker.strip()]

TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
SCHEDULE_START_HOUR = int(os.getenv("SCHEDULE_START_HOUR", "7"))
SCHEDULE_END_HOUR = int(os.getenv("SCHEDULE_END_HOUR", "19"))

# Alpaca API
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_PAPER = os.getenv("ALPACA_PAPER", "True").lower() in ("true", "1", "yes")
