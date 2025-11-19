# tradeGround/alpaca_request.py

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
import os
from decimal import Decimal
from datetime import datetime, timedelta, timezone
import pandas as pd

ALPACA_API_KEY_ID = os.getenv('ALPACA_API_KEY_ID')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

client = StockHistoricalDataClient(ALPACA_API_KEY_ID, ALPACA_SECRET_KEY)


def fetch_latest_price(symbol):
    symbol = symbol.upper().strip()
    if not symbol:
        return None
    
    try:
        request_params = StockLatestTradeRequest(symbol_or_symbols=[symbol])
        latest_trade = client.get_stock_latest_trade(request_params)

        if not latest_trade:
            return None
    
        return latest_trade[symbol].price
    
    except Exception as e:
        print(f"Error fetching latest price for {symbol}: {e}")
        return None


def fetch_price_history(symbol: str, days: int = 14):
    """
    Fetch recent daily bars for `symbol` from Alpaca and return:

        [{"time": "YYYY-MM-DD", "price": float}, ...]

    which is exactly what charts.js expects.
    """
    symbol = symbol.upper().strip()
    if not symbol:
        return []

    try:
        end = datetime.now(timezone.utc)
        # bit of buffer for weekends/holidays
        start = end - timedelta(days=days + 7)

        req = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
            feed=DataFeed.IEX,        # use free IEX feed, not SIP
        )

        bars = client.get_stock_bars(req)

        df = bars.df  # pandas DataFrame
        if df.empty:
            print(f"No bars returned from Alpaca for {symbol} (IEX)")
            return []

        try:
            sym_df = df.xs(symbol, level=0)
        except Exception:
            sym_df = df

        sym_df = sym_df.tail(days)

        history = []
        for idx, row in sym_df.iterrows():
            if isinstance(idx, pd.Timestamp):
                date_str = idx.date().isoformat()
            else:
                date_str = str(idx)[:10]

            close_price = row.get("close") or row.get("c")
            if close_price is None:
                continue

            history.append({
                "time": date_str,
                "price": float(Decimal(str(close_price))),
            })

        history.sort(key=lambda p: p["time"])
        return history[-days:]

    except Exception as e:
        print(f"Error fetching price history for {symbol}: {e}")
        return []


def fetch_intraday_history(symbol: str, hours: int = 24):
    """
    Fetch recent intraday bars (minute) for `symbol` from Alpaca IEX feed.

    Returns:
        [{"time": "YYYY-MM-DDTHH:MM", "price": float}, ...]
    """
    symbol = symbol.upper().strip()
    if not symbol:
        return []

    try:
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=hours + 2)  # small buffer

        req = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Minute,
            start=start,
            end=end,
            feed=DataFeed.IEX,
        )

        bars = client.get_stock_bars(req)
        df = bars.df
        if df.empty:
            print(f"No intraday bars returned from Alpaca for {symbol}")
            return []

        try:
            sym_df = df.xs(symbol, level=0)
        except Exception:
            sym_df = df

        # keep only last N minutes (roughly hours*60; df.tail is fine)
        sym_df = sym_df.tail(hours * 60)

        history = []
        for idx, row in sym_df.iterrows():
            if isinstance(idx, pd.Timestamp):
                time_str = idx.isoformat(timespec="minutes")
            else:
                time_str = str(idx)[:16]  # "YYYY-MM-DDTHH:MM"

            close_price = row.get("close") or row.get("c")
            if close_price is None:
                continue

            history.append({
                "time": time_str,
                "price": float(Decimal(str(close_price))),
            })

        history.sort(key=lambda p: p["time"])
        return history

    except Exception as e:
        print(f"Error fetching intraday history for {symbol}: {e}")
        return []
