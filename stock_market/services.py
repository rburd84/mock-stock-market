from .models import Stock

def simulate_market_tick():
    """ Loop through stocks and simulate market fluctuation """

    # Query database stocks
    all_stocks = Stock.objects.all()

    # Loop and fluctuate price
    for stock in all_stocks:
        stock.update_market_price()

    return f"Successfully updated {all_stocks.count()} stocks"