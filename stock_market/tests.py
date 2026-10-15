from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Stock, UserProfile, PortfolioHolding, Transaction


class StockMarketTradingTests(TestCase):

    def setUp(self):
        """ Set up mock data for testing purposes """
        # Create a dummy base Django user and profile
        self.user = User.objects.create_user(username='testtrader',  password='pasword123')
        self.profile = UserProfile.objects.create(user=self.user, cash_balance=Decimal("1000.00"))

        # Create a mock stock (Apple) priced at $150.00
        self.apple_stock = Stock.objects.create(
            ticker="AAPL",
            company_name="Apple Inc.",
            current_price=Decimal("150.00")
        )

    def test_successful_stock_purchase(self):
        """ Verifies a valid purchase, updates cash, holdings, and records transaction """
        # Buy 2 shares of Apple ($150 * 2 = $300 total cost)
        result_message = self.profile.buy_stock(self.apple_stock, quantity=2)

        # Re-fetch state from database to verify changes
        self.profile.refresh_from_db()
        holding = PortfolioHolding.objects.get(user_profile=self.profile, stock=self.apple_stock)
        latest_transaction = Transaction.objects.latest('timestamp')

        # Assertions to prove the system works
        self.assertEqual(self.profile.cash_balance, Decimal("700.00")) # $1000 - $300
        self.assertEqual(holding.shares_owned, 2)
        self.assertEqual(holding.average_buy_price, Decimal("150.00"))

        # Verify history ledger recorded
        self.assertEqual(latest_transaction.transaction_type, "BUY")
        self.assertEqual(latest_transaction.shares_quantity, 2)
        self.assertEqual(latest_transaction.price_per_share, Decimal("150.00"))

    def test_insufficient_funds(self):
        """ Verifies that insufficient funds throws an error """
        # Attempting to buy 10 shares cost $1500
        with self.assertRaises(ValidationError):
            self.profile.buy_stock(self.apple_stock, quantity=10)

        # Refetch profile
        self.profile.refresh_from_db()

        # Assert that database state rolled back completely
        self.assertEqual(self.profile.cash_balance, Decimal("1000.00"))
        self.assertFalse(PortfolioHolding.objects.filter(user_profile=self.profile, stock=self.apple_stock).exists())
        self.assertEqual(Transaction.objects.count(), 0)

    def test_invalid_quantity_fails(self):
        """ Verifies buying 0 or negative shares fails """
        with self.assertRaises(ValidationError):
            self.profile.buy_stock(self.apple_stock, quantity=0)

        with self.assertRaises(ValidationError):
            self.profile.buy_stock(self.apple_stock, quantity=-5)



















