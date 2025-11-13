from decimal import Decimal
from django.conf import settings
from django.db import models

class Profiles(models.Model):
    # Use Django's built-in User as the User's table
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
    on_delete=models.CASCADE, related_name="profile")

    current_cash_balance = models.DecimalField(max_digits=10,
    decimal_places=2, default=Decimal("10000.00"))

    def __str__(self):
        return f"{self.user.username} Profile"
    
    def sub_wallet(self, amount):
        self.current_cash_balance -= amount
        self.save()

    def add_wallet(self, amount):
        self.current_cash_balance += amount
        self.save()