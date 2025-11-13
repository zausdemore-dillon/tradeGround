from django.urls import path

from buy import views

app_name = 'buy'

urlpatterns = [
    path('', views.index, name='buy'),
    path('get_ticker', views.get_ticker, name='get_ticker'),
    path('checkout', views.checkout, name='checkout'),
]