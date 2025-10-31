from decimal import Decimal 
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from accounts.models import Profiles

User = get_user_model()

@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        # Initialize profile with a $10,000 starting balance
        Profiles.objects.create(
            user=instance, 
            current_cash_balance=Decimal("10000.00"),
            )