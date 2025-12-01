from django.urls import path

from . import views

urlpatterns = [
    path("api/holdings/prices/", views.holdings_prices_api, name="holdings_prices_api"),
    path("api/price-history/<str:symbol>/", views.price_history, name="price_history"),
    path("api/portfolio-history/", views.portfolio_history, name="portfolio_history"),
]