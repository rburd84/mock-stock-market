from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Stock, UserProfile, PortfolioHolding, Transaction
from .services import simulate_market_tick


class StockMarketTradingTests(TestCase):

    def setUp(self):
        """ Set up mock data for testing purposes """
        # Create a dummy base Django user and profile
        self.user = User.objects.create_user(username='testtrader',  password='pasword123')
        # self.profile = UserProfile.objects.create(user=self.user, cash_balance=Decimal("1000.00"))

        self.profile = self.user.profile
        self.profile.cash_balance = Decimal("1000.00")
        self.profile.save()

        # Create a mock stock (Apple) priced at $150.00
        self.apple_stock = Stock.objects.create(
            ticker="AAPL",
            company_name="Apple Inc.",
            current_price=Decimal("150.00"),
            current_daily_high=Decimal("150.00"),
            current_daily_low=Decimal("150.00")
        )

    """ Testing Buying Stock """
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


            """ Testing selling Stock """

    def test_successful_stock_sell(self):
        """ Verifies a stock selling """

        # Simulate stock buy
        PortfolioHolding.objects.create(user_profile=self.profile,
                                        stock=self.apple_stock,
                                        shares_owned=4,
                                        average_buy_price=Decimal("150.00"))
        print("\nProfile", self.profile.cash_balance)
        starting_cash = self.profile.cash_balance
        cash_from_sale = starting_cash + (3 * self.apple_stock.current_price)

        result_message = self.profile.sell_stock(self.apple_stock, quantity=3)
        print(result_message)

        latest_transaction = Transaction.objects.latest('timestamp')

        self.profile.refresh_from_db()

        holding = PortfolioHolding.objects.get(user_profile=self.profile, stock=self.apple_stock)
        print("Portfolio Holdings", holding)
        print("starting_cash", starting_cash)
        print("cash_from_sale", cash_from_sale)

        self.assertEqual(self.profile.cash_balance, starting_cash + 3 * self.apple_stock.current_price)
        self.assertEqual(holding.shares_owned, 1)
        self.assertEqual(latest_transaction.transaction_type, "SELL")
        self.assertEqual(latest_transaction.shares_quantity, 3)

    def test_cannot_sell_unowned_stock(self):
        tesla_stock = Stock.objects.create(
            ticker="TSLA",
            company_name="Tesla Inc.",
            current_price=Decimal("200.00"),
            current_daily_high=Decimal("200.00"),
            current_daily_low=Decimal("200.00")
        )
        starting_cash = self.profile.cash_balance

        with self.assertRaises(ValidationError):
            self.profile.sell_stock(tesla_stock, quantity=10)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.cash_balance, starting_cash)

    def test_cannot_oversell_shares(self):
        """Verifies that a user cannot sell more shares than they currently own."""
        # 1. Setup pre-condition state: user owns exactly 2 shares of Apple
        PortfolioHolding.objects.create(
            user_profile=self.profile,
            stock=self.apple_stock,
            shares_owned=2,
            average_buy_price=Decimal("150.00")
        )
        starting_cash = self.profile.cash_balance

        # 2. ASSERTION: Trying to sell 10 shares when they only own 2 must throw an error
        with self.assertRaises(ValidationError):
            self.profile.sell_stock(self.apple_stock, quantity=10)

        # 3. Verify state rolled back cleanly and cash didn't shift
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.cash_balance, starting_cash)



        """ Testing selling Stock """

    def test_market_price_fluctuation(self):
        """ Verifies market ticks change price """
        # Capture initial baseline
        original_price = self.apple_stock.current_price

        # Trigger market tick service
        simulate_market_tick()

        # Pull updated data
        self.apple_stock.refresh_from_db()
        new_price = self.apple_stock.current_price

        if new_price == original_price:
            simulate_market_tick()
            self.apple_stock.refresh_from_db()
            new_price = self.apple_stock.current_price

        # Verify Price movement
        self.assertNotEqual(original_price, new_price)

        # Verify movement within constraints
        max_allowed_price = original_price * Decimal("1.02")
        min_allowed_price = original_price * Decimal("0.98")

        self.assertLessEqual(new_price, max_allowed_price)
        self.assertGreaterEqual(new_price, min_allowed_price)

    def test_stock_price_floor(self):
        """ Ensure stock price never drops below $0.01 """
        penny_stock = Stock.objects.create(
            ticker="PNY",
            company_name="Penny Inc.",
            current_price=Decimal("0.02"),
            current_daily_high=Decimal("0.02"),
            current_daily_low=Decimal("0.02")
        )

        for _ in range(20):
            penny_stock.update_market_price(max_volatility=0.50)

        penny_stock.refresh_from_db()

        self.assertGreaterEqual(penny_stock.current_price, Decimal("0.01"))

    def test_daily_high_low_tracking(self):
        """ Verifies maximum high and low points are tracked accurately """
        volatile_stock = Stock.objects.create(
            ticker="VLT",
            company_name="Volatility Inc.",
            current_price=Decimal("100.00"),
            current_daily_high=Decimal("100.00"),
            current_daily_low=Decimal("100.00")
        )

        volatile_stock.current_price = Decimal("150.00")
        if volatile_stock.current_price > volatile_stock.current_daily_high:
            volatile_stock.current_daily_high = volatile_stock.current_price
        volatile_stock.save()

        volatile_stock.current_price = Decimal("50.00")
        if volatile_stock.current_price < volatile_stock.current_daily_low:
            volatile_stock.current_daily_low = volatile_stock.current_price
        volatile_stock.save()

        volatile_stock.current_price = Decimal("95.00")
        volatile_stock.save()

        volatile_stock.refresh_from_db()
        self.assertEqual(volatile_stock.current_daily_high, Decimal("150.00"))
        self.assertEqual(volatile_stock.current_daily_low, Decimal("50.00"))
        self.assertEqual(volatile_stock.current_price, Decimal("95.00"))

    def test_cost_basis_recalculation(self):
        self.profile.cash_balance = Decimal("5000.00")
        self.profile.save()

        # Total cost: $1,500.00
        self.profile.buy_stock(self.apple_stock, quantity=10)
        self.apple_stock.save()

        self.apple_stock.current_price = Decimal("180.00")
        self.apple_stock.save()

        # Additional cost: 5 * $180 = $900.00
        self.profile.buy_stock(self.apple_stock, quantity=5)

        holding = PortfolioHolding.objects.get(user_profile=self.profile, stock=self.apple_stock)

        # Total Shares = 10 + 5 = 15
        # Total Spent = $1,500 + $900 = $2,400
        # Expected Average Cost Basis = $2,400 / 15 = $160.00
        self.assertEqual(holding.shares_owned, 15)
        self.assertEqual(holding.average_buy_price, Decimal("160.00"))




























