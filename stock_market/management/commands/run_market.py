import time
from django.core.management.base import BaseCommand
from django.utils import timezone

# Absolute imports based on your app name:
from stock_market.models import Stock
from stock_market.services import simulate_market_tick

class Command(BaseCommand):
    help = ("Runs a continuos terminal loop to simulate live stock "
            "market price fluctuations.")

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("★ Mock Stock Market Simulation Started ★"))
        self.stdout.write("Press Ctrl+C to stop the simulation.\n")

        try:
            while True:
                # Capture the timestamp of current tick
                current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

                # Trigger market service
                simulate_market_tick()

                # Build text dashboard in terminal
                self.stdout.write(f"=== Market Tick Summary [{current_time}] ===")

                all_stocks = Stock.objects.all()
                for stock in all_stocks:
                    self.stdout.write(f"  • {stock.ticker:<5} | {stock.company_name:<20} | Price: ${stock.current_price:.2f}")

                self.stdout.write("-" * 50 + "\n")

                # Pause execution
                time.sleep(2)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n✕ Market simulation stopped by user."))

