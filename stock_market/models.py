from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction


class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.ticker} - {self.company_name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)

    def buy_stock(self, stock, quantity):
        """ Execute a stock purchase, deduct cash, update
        holdings and log transaction record """

        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")

        total_cost = stock.current_price * quantity

        if self.cash_balance < total_cost:
            raise ValidationError(f"Insufficient funds. Required: ${total_cost}, Available: ${self.cash_balance}")

        # Data integrity
        with transaction.atomic():
            # Deduct cash
            self.cash_balance -= total_cost
            self.save()

            # Retrieve existing holdings or prepare a blank one
            holding, created = PortfolioHolding.objects.get_or_create(
                user_profile=self,
                stock=stock,
                defaults={'shares_owned': 0, 'average_buy_price': Decimal(0.00)}
            )

            # Holding method to update shares and average price
            holding.add_shares(quantity, stock.current_price)

            # Log transaction into history ledger
            Transaction.objects.create(
                user_profile=self,
                stock=stock,
                transaction_type='BUY',
                shares_quantity=quantity,
                price_per_share=stock.current_price
            )

        return f"Successfully brought {quantity} shares of {stock.ticker}."

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

    def add_shares(self, new_quantity, execution_price):
        """ Update total shares owned and recalculate the average cost """
        total_shares = self.shares_owned + new_quantity

        # Calculate new weighted average cost basis
        current_total_cost = self.shares_owned * self.average_buy_price
        new_total_cost = new_quantity * execution_price

        self.average_buy_price = (current_total_cost + new_total_cost) / total_shares
        self.shares_owned = total_shares
        self.save()

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
