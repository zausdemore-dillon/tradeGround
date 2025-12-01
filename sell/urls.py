from django.urls import path
from sell import views

app_name = "sell"

urlpatterns = [
    path("", views.SellView.as_view(), name="sell"),
]