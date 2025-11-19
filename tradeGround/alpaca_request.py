from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
import os
from decimal import Decimal
from datetime import datetime, timedelta, timezone
import pandas as pd

# Read Alpaca API credentials from environment variables
ALPACA_API_KEY_ID = os.getenv('ALPACA_API_KEY_ID')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

# Create a single reusable Alpaca data client
client = StockHistoricalDataClient(ALPACA_API_KEY_ID, ALPACA_SECRET_KEY)


def fetch_latest_price(symbol):
    """Return the latest trade price of a stock symbol."""
    symbol = symbol.upper().strip()
    if not symbol:
        return None

    try:
        # Build request object for Alpaca latest trade endpoint
        request_params = StockLatestTradeRequest(symbol_or_symbols=[symbol])

        # Fetch the latest trade for the symbol
        latest_trade = client.get_stock_latest_trade(request_params)

        if not latest_trade:
            return None

        # Access the price inside the returned dictionary
        return latest_trade[symbol].price

    except Exception as e:
        print(f"Error fetching latest price for {symbol}: {e}")
        return None


def fetch_price_history(symbol: str, days: int = 14):
    """
    Fetch recent *daily* bars for a symbol.

    Returns list of dicts:
        [{"time": "YYYY-MM-DD", "price": float}, ...]
    """
    symbol = symbol.upper().strip()
    if not symbol:
        return []

    try:
        # Determine date range — extra buffer for weekends/holidays
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days + 7)

        # Build request object for daily bars
        req = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
            feed=DataFeed.IEX,  # Free data feed
        )

        # Query Alpaca for daily price bars
        bars = client.get_stock_bars(req)
        df = bars.df
        if df.empty:
            print(f"No bars returned from Alpaca for {symbol} (IEX)")
            return []

        # Some Alpaca responses use a multiindex (symbol, timestamp)
        try:
            sym_df = df.xs(symbol, level=0)  # Extract symbol-specific rows
        except Exception:
            sym_df = df  # Fallback when index is flat

        # Keep only the most recent N days
        sym_df = sym_df.tail(days)

        history = []
        for idx, row in sym_df.iterrows():
            # Convert index to simple date string
            if isinstance(idx, pd.Timestamp):
                date_str = idx.date().isoformat()
            else:
                date_str = str(idx)[:10]

            # Alpaca sometimes returns "close" or "c"
            close_price = row.get("close") or row.get("c")
            if close_price is None:
                continue

            # Convert price to float with Decimal for safety
            history.append({
                "time": date_str,
                "price": float(Decimal(str(close_price))),
            })

        # Sort by date and return exactly `days` entries
        history.sort(key=lambda p: p["time"])
        return history[-days:]

    except Exception as e:
        print(f"Error fetching price history for {symbol}: {e}")
        return []


def fetch_intraday_history(symbol: str, hours: int = 24):
    """
    Fetch *minute-by-minute* intraday bars for a symbol.

    Returns list of dicts:
        [{"time": "YYYY-MM-DDTHH:MM", "price": float}, ...]
    """
    symbol = symbol.upper().strip()
    if not symbol:
        return []

    try:
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=hours + 2)  # Slight buffer to cover missing minutes

        # Build request object for minute bars
        req = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Minute,
            start=start,
            end=end,
            feed=DataFeed.IEX,
        )

        # Query Alpaca for minute-level price bars
        bars = client.get_stock_bars(req)
        df = bars.df
        if df.empty:
            print(f"No intraday bars returned from Alpaca for {symbol}")
            return []

        # Extract symbol-level data if multiindex
        try:
            sym_df = df.xs(symbol, level=0)
        except Exception:
            sym_df = df

        # Keep only the last N minutes (hours * 60)
        sym_df = sym_df.tail(hours * 60)

        history = []
        for idx, row in sym_df.iterrows():
            # Format timestamp as ISO down to minutes
            if isinstance(idx, pd.Timestamp):
                time_str = idx.isoformat(timespec="minutes")
            else:
                time_str = str(idx)[:16]

            close_price = row.get("close") or row.get("c")
            if close_price is None:
                continue

            history.append({
                "time": time_str,
                "price": float(Decimal(str(close_price))),
            })

        # Sort by time so Charts.js can plot it properly
        history.sort(key=lambda p: p["time"])
        return history

    except Exception as e:
        print(f"Error fetching intraday history for {symbol}: {e}")
        return []

