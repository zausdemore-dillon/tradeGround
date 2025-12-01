"""
URL configuration for tradeGround project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from decimal import Decimal

from trades.models import Holdings
from tradeGround.alpaca_request import fetch_latest_price


def home(request):
    balance = None
    portfolio_value = None
    portfolio_roi_pct = None

    if request.user.is_authenticated:
        # CASH BALANCE (from profile) 
        try:
            balance = request.user.profile.current_cash_balance
        except Exception:
            balance = Decimal("0.00")

        # HOLDINGS (portfolio value + ROI, excludes cash) 
        holdings = Holdings.objects.filter(user=request.user, quantity__gt=0)

        if holdings.exists():
            total_value = Decimal("0")
            total_cost_basis = Decimal("0")

            for h in holdings:
                latest_price = fetch_latest_price(h.ticker)
                if latest_price is None:
                    continue

                qty = h.quantity
                latest_dec = Decimal(str(latest_price))

                # current market value of this holding
                total_value += qty * latest_dec

                # cost basis of this holding
                total_cost_basis += qty * h.avg_cost_basis

            portfolio_value = total_value

            if total_cost_basis > 0:
                portfolio_roi_pct = (
                    (total_value - total_cost_basis)
                    / total_cost_basis
                    * Decimal("100")
                )

    context = {
        "balance": balance,                    # cash only (from Profiles via user.profile)
        "portfolio_value": portfolio_value,    # holdings only (no cash)
        "portfolio_roi_pct": portfolio_roi_pct # overall unrealized ROI %
    }
    return render(request, "home.html", context)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("trades/", include("trades.urls")),
    path("", home, name="home"),
    path("sell/", include("sell.urls")),
    path("buy/", include('buy.urls')),
]