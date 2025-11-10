from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/holdings/prices/", views.holdings_prices_api, name="holdings_prices_api"),
]