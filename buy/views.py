from django.shortcuts import render
from alpaca.data.live.stock import StockDataStream
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, redirect
from tradeGround.alpaca_request import fetch_latest_price
import json
from trades.models import Trades
from accounts.models import Profiles
from django.contrib.auth import get_user_model
from trades.services import Services
# Create your views here.
ALPACA_API_KEY_ID="PKGAL7OJYM5ECHEBFDLKSHTPNY"
ALPACA_SECRET_KEY="CLzJ64jhc4qbMbqYbejub66vVwYtZrknvpW5THRS2ySa"
ALPACA_BASE_URL="https://paper-api.alpaca.markets/v2"

def index(request):
    return render(request, "../templates/buy.html")

def get_ticker(request):
    symbol = request.GET['ticker']
    #lookup ticker in request
    price = fetch_latest_price(symbol)
    if price:
        return HttpResponse(json.dumps({"ticker":request.GET['ticker'], "price":price, "exists":True}))
    #return True if found else false
    return HttpResponse('{"exists":false}')

def checkout(request):
    service = Services()
    #get data from cart
    trades = json.loads(request.body)
    for symbol in trades:
        service.buy_stock(request.user, symbol, trades[symbol]['amount'])
        
    return HttpResponse(status=200)
    


