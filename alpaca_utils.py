import alpaca_trade_api as tradeapi
from django.conf import settings

def get_alpaca_client():
    """Initialize and return Alpaca API client"""
    return tradeapi.REST(
        settings.ALPACA_API_KEY,
        settings.ALPACA_SECRET_KEY,
        settings.ALPACA_BASE_URL,
        api_version='v2'
    )

def get_stock_price(symbol):
    """Get current price for a stock symbol"""
    api = get_alpaca_client()
    try:
        # Get latest trade
        trade = api.get_latest_trade(symbol)
        return float(trade.price)
    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return None

def get_account_info():
    """Get account information (buying power, equity, etc.)"""
    api = get_alpaca_client()
    try:
        account = api.get_account()
        return {
            'buying_power': float(account.buying_power),
            'equity': float(account.equity),
            'cash': float(account.cash)
        }
    except Exception as e:
        print(f"Error getting account info: {e}")
        return None

def get_positions():
    """Get all current stock positions"""
    api = get_alpaca_client()
    try:
        positions = api.list_positions()
        return [{
            'symbol': pos.symbol,
            'qty': float(pos.qty),
            'avg_entry_price': float(pos.avg_entry_price),
            'current_price': float(pos.current_price),
            'market_value': float(pos.market_value),
            'profit_loss': float(pos.unrealized_pl)
        } for pos in positions]
    except Exception as e:
        print(f"Error getting positions: {e}")
        return []

def sell_stock(symbol, quantity):
    """Sell a specified quantity of stock"""
    api = get_alpaca_client()
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=quantity,
            side='sell',
            type='market',
            time_in_force='gtc'  # Good 'til canceled
        )
        return {
            'success': True,
            'order_id': order.id,
            'symbol': order.symbol,
            'qty': order.qty,
            'side': order.side
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
