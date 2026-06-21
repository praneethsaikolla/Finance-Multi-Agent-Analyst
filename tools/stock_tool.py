import yfinance as yf
import pandas as pd
from crewai.tools import tool

@tool("stock_tool")
def stock_tool(ticker: str) -> str:
    """
    Fetches the latest stock data for a given ticker and returns a structured summary
    of price action, technical indicators, trend direction, and volume behavior.
    """
    try:
        stock = yf.Ticker(ticker)
        try:
            current_price = stock.fast_info['lastPrice']
            previous_close = stock.fast_info['previousClose']
        except Exception:
            current_price = None
            previous_close = None

        df = stock.history(period="60d", interval="15m", actions=False)
        if df.empty:
            if current_price is not None:
                return f"ticker: {ticker}\ncurrent_price: ${current_price:.2f}\nError: History data unavailable for indicators."
            return f"Error: No data found for ticker '{ticker}'. It may be delisted or invalid."

        df = df.dropna(subset=['Close'])
        if df.empty:
            if current_price is not None:
                return f"ticker: {ticker}\ncurrent_price: ${current_price:.2f}\nError: Usable price data unavailable for indicators."
            return f"Error: No usable price data available for ticker '{ticker}'."

        # Calculate RSI (14)
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Calculate MACD (12, 26, 9)
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # Calculate SMA and EMA (20)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()

        # Bollinger Bands (20, 2)
        std_20 = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['SMA_20'] + (std_20 * 2)
        df['BB_Lower'] = df['SMA_20'] - (std_20 * 2)

        # Volume average
        df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()

        latest = df.iloc[-1]
        current_price = current_price if current_price is not None else latest['Close']
        if previous_close is None and len(df) >= 2:
            previous_close = df.iloc[-2]['Close']
        rsi = latest['RSI']
        macd = latest['MACD']
        signal = latest['Signal']
        sma_20 = latest['SMA_20']
        ema_20 = latest['EMA_20']
        bb_upper = latest['BB_Upper']
        bb_lower = latest['BB_Lower']
        vol_avg = latest['Vol_SMA_20']
        vol_current = latest['Volume']

        if pd.notna(previous_close) and previous_close != 0:
            change_1d = ((current_price - previous_close) / previous_close) * 100
        else:
            change_1d = None

        if pd.isna(sma_20) or pd.isna(ema_20):
            trend_direction = "N/A — data unavailable"
        elif current_price > sma_20 and current_price > ema_20:
            trend_direction = "Uptrend"
        elif current_price < sma_20 and current_price < ema_20:
            trend_direction = "Downtrend"
        else:
            trend_direction = "Sideways"

        if pd.notna(macd) and pd.notna(signal):
            if macd > signal:
                macd_signal = "Bullish crossover"
            elif macd < signal:
                macd_signal = "Bearish crossover"
            else:
                macd_signal = "No clear crossover"
        else:
            macd_signal = "N/A — data unavailable"

        if pd.notna(bb_upper) and pd.notna(bb_lower):
            if current_price > bb_upper:
                bb_position = "Above upper band"
            elif current_price < bb_lower:
                bb_position = "Below lower band"
            elif current_price >= (bb_upper + bb_lower) / 2:
                bb_position = "Upper band area"
            else:
                bb_position = "Lower band area"
        else:
            bb_position = "N/A — data unavailable"

        volume_spike = (
            "Yes" if pd.notna(vol_avg) and vol_current > 1.5 * vol_avg else "No"
        )

        summary = [
            f"ticker: {ticker}",
            f"current_price: ${current_price:.2f}",
            f"previous_close: ${previous_close:.2f}" if pd.notna(previous_close) else "previous_close: N/A",
            f"change_1d_pct: {change_1d:.2f}%" if change_1d is not None else "change_1d_pct: N/A",
            f"trend_direction: {trend_direction}",
            f"rsi: {rsi:.2f}" if pd.notna(rsi) else "rsi: N/A",
            f"macd: {macd:.4f}" if pd.notna(macd) else "macd: N/A",
            f"signal: {signal:.4f}" if pd.notna(signal) else "signal: N/A",
            f"macd_signal: {macd_signal}",
            f"sma_20: ${sma_20:.2f}" if pd.notna(sma_20) else "sma_20: N/A",
            f"ema_20: ${ema_20:.2f}" if pd.notna(ema_20) else "ema_20: N/A",
            f"bb_upper: ${bb_upper:.2f}" if pd.notna(bb_upper) else "bb_upper: N/A",
            f"bb_lower: ${bb_lower:.2f}" if pd.notna(bb_lower) else "bb_lower: N/A",
            f"bb_position: {bb_position}",
            f"volume_current: {int(vol_current)}",
            f"volume_avg_20: {int(vol_avg)}" if pd.notna(vol_avg) else "volume_avg_20: N/A",
            f"volume_spike: {volume_spike}",
        ]

        return "\n".join(summary)
    except Exception as e:
        return f"Error fetching stock data for {ticker}: {str(e)}"
