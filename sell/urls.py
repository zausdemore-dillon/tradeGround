from django.urls import path
from sell import views

app_name = "sell"

urlpatterns = [
    path("", views.sell_view, name="sell"),
]