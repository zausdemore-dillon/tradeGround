from decimal import Decimal
from datetime import date, timedelta

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from tradeGround.alpaca_request import fetch_price_history, fetch_intraday_history
from .models import Holdings, Trades

def index(request):
    return HttpResponse("Hello, world. You're at the trades index.")

@login_required
def holdings_prices_api(request):
    """
    Return latest prices for each holding the user owns.
    Used by pullShareValues.js to fill in the holdings table.
    """
    symbols = Holdings.objects.filter(user=request.user).values_list('ticker', flat=True).distinct()

    data = {}

    for s in symbols:
        price = fetch_latest_price(s)
        if price is not None:
            data[s] = str(price)
        else:
            data[s] = None

    return JsonResponse(data)

def price_history(request, symbol):
    """
    Price history endpoint with range support.

    Query param:
      ?range=1D | 1W | 1M | 1Y
    """
    symbol = symbol.upper()
    range_key = (request.GET.get("range") or "1D").upper()

    # map ranges to type + window
    RANGE_CONFIG = {
        "1D": {"type": "intraday", "hours": 24},
        "1W": {"type": "daily", "days": 7},
        "1M": {"type": "daily", "days": 30},
        "1Y": {"type": "daily", "days": 365},
        "5Y": {"type": "daily", "days": 365 * 5},
    }

    cfg = RANGE_CONFIG.get(range_key, RANGE_CONFIG["1D"])

    try:
        if cfg["type"] == "intraday":
            history = fetch_intraday_history(symbol, hours=cfg["hours"])
        else:
            history = fetch_price_history(symbol, days=cfg["days"])
    except Exception as e:
        print(f"Error in price_history for {symbol}, range {range_key}: {e}")
        history = []

    # optional: fallback synthetic data so UI always has a line
    if not history:
        if cfg["type"] == "intraday":
            # simple 24-point synthetic intraday series
            points = cfg["hours"]
            base_price = 100.0
            now = datetime.now(timezone.utc)
            data = []
            for i in range(points):
                t = now - timedelta(hours=points - i)
                base_price += (i % 3 - 1) * 0.2
                data.append({
                    "time": t.isoformat(timespec="minutes"),
                    "price": round(base_price, 2),
                })
            history = data
        else:
            days = cfg["days"]
            today = date.today()
            base_price = 110.0
            data = []
            for i in range(days):
                day = today - timedelta(days=days - i)
                base_price += (i % 3 - 1) * 0.8
                data.append({
                    "time": day.strftime("%Y-%m-%d"),
                    "price": round(base_price, 2),
                })
            history = data

    return JsonResponse(history, safe=False)
    
@login_required
def portfolio_history(request):
    """
    Build a portfolio value time series for logged-in users
    by replaying their trades in timestamp order.

    Uses Trades model:

        Trades.user             : FK to User
        Trades.side             : "BUY" or "SELL"
        Trades.ticker           : str (symbol)
        Trades.shares           : Decimal (shares, >0)
        Trades.exec_price       : Decimal (price >0)
        Trades.exec_timestamp   : DateTime of execution
    """
    user = request.user

    # Paper trading starting cash
    initial_cash = Decimal("10000.00")

    trades_qs = (
        Trades.objects
        .filter(user=user)
        .order_by("exec_timestamp")
    )

    if not trades_qs.exists():
        now = timezone.now().isoformat(timespec="seconds")
        return JsonResponse(
            [{"time": now, "value": float(initial_cash)}],
            safe=False,
        )
    
    cash = initial_cash
    positions = {}      # ticker -> quantity
    last_price = {}     # ticker -> last trade price
    series = []

    for trade in trades_qs:
        ticker = trade.ticker
        qty = trade.shares
        side = trade.side.upper()
        price = trade.exec_price
        ts = trade.exec_timestamp

        # BUY adds to position / reduces cash, SELL reduces position / adds cash
        signed_qty = qty if side == Trades.BUY else -qty

        cash -= signed_qty * price
        positions[ticker] = positions.get(ticker, Decimal("0")) + signed_qty
        last_price[ticker] = price

        # compute portfolio value at this point in time
        positions_value = Decimal("0")
        for sym, q in position.items():
            if q == 0:
                continue
            p = last_price.get(sym, Decimal("0"))
            positions_value += q * p
        
        total_value = cash + positions_value

        series.append({
            "time": ts.isoformat(timespec="seconds"),
            "value": float(total_value),
        })
    
    return JsonResponse(series, safe=False)
