from decimal import Decimal
from datetime import date, datetime, timedelta

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Alpaca data-fetch helpers
from tradeGround.alpaca_request import (
    fetch_latest_price,
    fetch_price_history,
    fetch_intraday_history,
)

from .models import Holdings


def price_history(request, symbol):
    """
    Return historical price data for a symbol.
    Range determined by ?range=1D/1W/1M/1Y/5Y.
    """
    symbol = symbol.upper().strip()
    if not symbol:
        return JsonResponse([], safe=False)

    # Determine date range (default: 1D)
    range_key = (request.GET.get("range") or "1D").upper()

    # Map UI ranges → fetch parameters
    RANGE_CONFIG = {
        "1D": {"type": "intraday", "hours": 24},
        "1W": {"type": "daily", "days": 7},
        "1M": {"type": "daily", "days": 30},
        "1Y": {"type": "daily", "days": 365},
        "5Y": {"type": "daily", "days": 365 * 5},
    }

    cfg = RANGE_CONFIG.get(range_key, RANGE_CONFIG["1D"])

    # Call correct Alpaca function based on intraday/daily
    if cfg["type"] == "intraday":
        history = fetch_intraday_history(symbol, hours=cfg["hours"])
    else:
        history = fetch_price_history(symbol, days=cfg["days"])

    return JsonResponse(history, safe=False)


@login_required
def holdings_prices_api(request):
    """
    Return latest market prices for all of the user's holdings.
    Output used by front-end JS for updating live share values.
    """
    # Get unique tickers for this user
    symbols = (
        Holdings.objects
        .filter(user=request.user)
        .values_list("ticker", flat=True)
        .distinct()
    )

    data = {}

    # Lookup each ticker's latest price
    for s in symbols:
        price = fetch_latest_price(s)
        data[s] = str(price) if price is not None else None

    return JsonResponse(data)


@login_required
def portfolio_history(request):
    """
    Compute total portfolio value over time using historical price data.
    Returns a time series list: [{"time": ..., "value": ...}, ...]
    """
    user = request.user

    # Determine requested time range (default: 1D)
    range_key = (request.GET.get("range") or "1D").upper()

    RANGE_CONFIG = {
        "1D": {"type": "intraday", "hours": 24},
        "1W": {"type": "daily", "days": 7},
        "1M": {"type": "daily", "days": 30},
        "1Y": {"type": "daily", "days": 365},
        "5Y": {"type": "daily", "days": 365 * 5},
    }
    cfg = RANGE_CONFIG.get(range_key, RANGE_CONFIG["1D"])

    # Get current holdings (assumes quantity constant over time)
    holdings = Holdings.objects.filter(user=user, quantity__gt=0)
    if not holdings.exists():
        return JsonResponse([], safe=False)

    # Map ticker → share count
    quantities = {h.ticker.upper(): float(h.quantity) for h in holdings}

    aggregate = {}  # Accumulates {timestamp → total portfolio value}

    # Build combined time series
    for ticker, qty in quantities.items():
        try:
            # Pull per-stock history based on selected range
            if cfg["type"] == "intraday":
                series = fetch_intraday_history(ticker, hours=cfg["hours"])
            else:
                series = fetch_price_history(ticker, days=cfg["days"])
        except Exception as e:
            print(f"Error fetching history for {ticker} in portfolio: {e}")
            series = []

        # Add each price point to aggregate timeseries
        for point in series:
            t = point["time"]
            v = qty * float(point["price"])  # shares × price
            aggregate[t] = aggregate.get(t, 0.0) + v

    # Convert dict → sorted list for JSON
    history = [
        {"time": t, "value": round(v, 2)}
        for t, v in sorted(aggregate.items())
    ]

    return JsonResponse(history, safe=False)
