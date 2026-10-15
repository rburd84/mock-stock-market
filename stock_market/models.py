from django.contrib.auth.models import User
from django.db import models


class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.ticker} - {self.company_name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)

    def __str__(self):
        return f"{self.user.username}'s profile"


class PortfolioHolding(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='holdings')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='portfolios')
    shares_owned = models.PositiveIntegerField(default=0)
    average_buy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        """ Eliminates duplicate entries """
        unique_together = ('user_profile', 'stock')

    def __str__(self):
        return f"{self.user_profile.username} owns {self.shares_owned} shares of {self.stock}"


class Transaction(models.Model):
    """ Record buy and sell transactions """
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transactions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    shares_quantity = models.PositiveIntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} | {self.shares_quantity} {self.stock.ticker} at ${self.price_per_share}"
