from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from tradeGround.alpaca_request import fetch_latest_price
from .models import Holdings

def index(request):
    return HttpResponse("Hello, world. You're at the trades index.")

@login_required
def holdings_prices_api(request):

    symbols = Holdings.objects.filter(user=request.user).values_list('ticker', flat=True).distinct()

    data = {}

    for s in symbols:
        price = fetch_latest_price(s)
        if price is not None:
            data[s] = str(price)
        else:
            data[s] = None

    return JsonResponse(data)
