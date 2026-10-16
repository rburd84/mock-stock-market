from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from decimal import Decimal
from stock_market.models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Create user profile and seed with cash """

    if created:
        UserProfile.objects.create(
            user=instance,
            cash_balance=Decimal("10000.00")
        )