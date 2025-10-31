# Routes the URL path /accounts/signup/ to our SignUpView.

from django.urls import path
from .views import SignUpView

urlpatterns = [
    # URL pattern for the signup page
    path("signup/", SignUpView.as_view(), name="signup"),
]