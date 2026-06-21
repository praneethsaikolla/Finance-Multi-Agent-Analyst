import os
import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from fin_agent.config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_PAPER

logger = logging.getLogger(__name__)

def execute_trade(ticker: str, action: str, qty: int = 1):
    """
    Executes a simulated paper trade on Alpaca based on the strategist's recommendation.
    """
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        logger.warning(f"Alpaca API keys are missing! Skipping simulated trade for {ticker}.")
        return {"status": "skipped", "reason": "No Alpaca credentials"}

    action_upper = action.upper().strip()
    if action_upper not in ["BUY", "SELL"]:
        logger.info(f"Action '{action}' is not BUY/SELL. No trade executed for {ticker}.")
        return {"status": "skipped", "reason": "Action is hold or invalid"}

    try:
        trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=ALPACA_PAPER)
        
        # Check if we have enough position to sell
        if action_upper == "SELL":
            try:
                position = trading_client.get_open_position(ticker)
                if int(position.qty) < qty:
                    logger.warning(f"Not enough {ticker} shares to sell.")
                    return {"status": "failed", "reason": "Insufficient position to sell"}
            except Exception:
                logger.warning(f"No existing position found for {ticker}. Cannot sell.")
                return {"status": "failed", "reason": "No position to sell"}

        side = OrderSide.BUY if action_upper == 'BUY' else OrderSide.SELL
        logger.info(f"Submitting Alpaca Paper Trade: {side.name} {qty} shares of {ticker}")
        
        market_order_data = MarketOrderRequest(
            symbol=ticker,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.GTC
        )
        order = trading_client.submit_order(order_data=market_order_data)
        
        logger.info(f"Order submitted successfully. Order ID: {order.id}")
        return {"status": "success", "order_id": str(order.id), "side": side.name, "qty": qty, "symbol": ticker}

    except Exception as e:
        logger.error(f"Alpaca trade execution failed for {ticker}: {str(e)}")
        return {"status": "error", "reason": str(e)}

def parse_and_execute_strategy(ticker: str, strategy_markdown: str):
    """
    Parses the Strategist agent's markdown output to find the exact 'Action:'
    If it recommends BUY or SELL, it triggers the execution module.
    """
    import re
    match = re.search(r"\**Action:\**\s*(BUY|SELL|HOLD)", strategy_markdown, re.IGNORECASE)
    
    if match:
        action = match.group(1).upper()
        logger.info(f"Strategist recommended {action} for {ticker}. Initiating execution flow...")
        return execute_trade(ticker, action=action, qty=1)
    else:
        logger.info(f"Could not parse a definitive BUY/SELL/HOLD action for {ticker}.")
        return {"status": "skipped", "reason": "Could not parse action"}
