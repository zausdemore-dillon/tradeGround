from django.urls import path

from buy import views

app_name = 'buy'

urlpatterns = [
    path('', views.index, name='buy'),
    path('validate', views.validate_symbol, name='validate'),
    path('checkout', views.checkout, name='checkout'),
    path('get_prices', views.get_prices, name='get_prices'),
    path('autocomplete', views.ajax_autocomplete, name='autocomplete'),
]