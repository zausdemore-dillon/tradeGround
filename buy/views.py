from django.shortcuts import render
from alpaca.data.live.stock import StockDataStream
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, redirect
from tradeGround.alpaca_request import fetch_latest_price
import json, re
from trades.models import Trades
from accounts.models import Profiles
from django.contrib.auth import get_user_model
from trades.services import Services
# Create your views here.

def index(request):
    return render(request, "../templates/buy.html")

def validate_symbol(request):
    #return true or false, needs ?ticker=AMZN
    symbol = request.GET['ticker']
    try:
        price = fetch_latest_price(symbol)
        if price:
            return HttpResponse(json.dumps({'exists':True, 'price':price}), status=200)
        else:
            return HttpResponse('{"exists":false}', status=404)
    except Exception as e:
        return HttpResponse(str(e), status=503)

def checkout(request):
    #get a list of tickers and their quantities to buy, returns success or failure
    service = Services()
    #get data from cart request.body = Dict[str, int] Dict[ticker, quantity]
    try:
        trades = json.loads(request.body)
        for symbol in trades:
            service.buy_stock(request.user, symbol, trades[symbol])
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(str(e), status=503)

def get_prices(request):
    #get a list of tickers and return their current prices or 503
    prices = []
    symbols: list[str] = json.loads(request.body)
    for symbol in symbols:
        price = fetch_latest_price(symbol)
        if not price:
            prices.append(None)
        else:
            prices.append(price)
    return HttpResponse(json.dumps(prices), status=200)

def ajax_autocomplete(request):
    #takes in a search term and returns symbols from holdings with matching prefixes
    #request needs ?prefix=[some prefix]
    try:
        prefix = request.GET['prefix']
        symbols = Trades.objects.values_list('ticker', flat=True).distinct()
        matches = []
        for symbol in symbols:
            match = re.findall(prefix, symbol)
            if len(match) > 0:
                print(match)
                matches.append(symbol)
        return HttpResponse(json.dumps(matches))
    except Exception as e:
        return HttpResponse(e, status=503)
    


