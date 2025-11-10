from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
import os

ALPACA_API_KEY_ID = os.getenv('ALPACA_API_KEY_ID')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

client = StockHistoricalDataClient(ALPACA_API_KEY_ID,ALPACA_SECRET_KEY)

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