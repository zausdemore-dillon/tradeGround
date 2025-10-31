from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm  # built-in form

class SignUpView(CreateView):
    """
    Handles new user registration using Django's default UserCreationForm.
    No custom form is required since we're only using username and password.
    """
    form_class = UserCreationForm                 # built-in Django form
    template_name = "registration/signup.html"    # HTML template for signup
    success_url = reverse_lazy("login")           # redirect to login page after success

    def form_valid(self, form):
        """
        Called when the form passes validation.
        Adds a success message and then creates the new user.
        """
        messages.success(self.request, "Account created! You can log in now.")
        return super().form_valid(form)
