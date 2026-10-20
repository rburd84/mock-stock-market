from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView

from stock_market.models import Stock, PortfolioHolding, Transaction


class MarketDashboardView(LoginRequiredMixin, ListView):
    """ List active market listings """
    model = Stock
    template_name = 'dashboard.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        return Stock.objects.all().order_by('ticker')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['profile'] = self.request.user.profile

        return context


class TradeFormEndpointView(LoginRequiredMixin, View):
    def get(self, request, ticker):
        # Fetch requested stock
        stock = get_object_or_404(Stock, ticker=ticker)

        # Extract context from buttons
        trade_type = request.GET.get('type', 'BUY').upper()

        holding = PortfolioHolding.objects.filter(user_profile=request.user.profile, stock=stock).first()
        shares_owned = holding.shares_owned if holding else 0

        context = {
            'stock': stock,
            'trade_type': trade_type,
            'profile': request.user.profile,
            'shares_owned': shares_owned,
        }

        return render(request, 'stock_market/partials/_trade_form.html', context)

    pass


class ExecuteTradeView(LoginRequiredMixin, View):
    def post(self, request):
        ticker = request.POST.get('ticker')
        trade_type = request.POST.get('trade_type', '').upper()

        try:
            quantity = int(request.POST.get('quantity', 0))
        except ValueError as e:
            messages.error(request, 'Invalid Entry. Quantity must be a whole number.')
            return redirect('market_dashboard')

        stock = get_object_or_404(Stock, ticker=ticker)
        user_profile = request.user.profile

        try:
            if trade_type == 'BUY':
                message = user_profile.buy_stock(stock, quantity)
            elif trade_type == 'SELL':
                message = user_profile.sell_stock(stock, quantity)
            else:
                raise ValidationError('Invalid order configuration.')

            messages.success(request, message)

        except ValidationError as e:
            messages.error(request, e.message)


        return redirect(request.META.get("HTTP_REFERER", "market_dashboard"))


class StockDetailView(LoginRequiredMixin, DetailView):
    model = Stock
    template_name = 'stock_detail.html'
    context_object_name = 'stock'
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_profile = self.request.user.profile
        current_stock = self.object

        holding = PortfolioHolding.objects.filter(
            user_profile=user_profile,
            stock=current_stock
        ).first()

        if holding:
            context['shares_owned'] = holding.shares_owned
            context['avg_buy_price'] = holding.average_buy_price

            total_cost_basis = holding.shares_owned * holding.average_buy_price
            current_market_value = holding.shares_owned * current_stock.current_price
            context['market_value'] = current_market_value
            context['unrealized_pnl'] = current_market_value - total_cost_basis
        else:
            context['shares_owned'] = 0
            context['avg_buy_price'] = 0
            context['market_value'] = 0
            context['unrealized_pnl'] = 0

        context['profile'] = user_profile

        return context


class UserPortfolio(LoginRequiredMixin, View):
    def get(self, request):
        user_profile = request.user.profile

        active_holdings = PortfolioHolding.objects.filter(
            user_profile=user_profile,
            shares_owned__gt=0
        ).select_related('stock')

        transaction_logs = Transaction.objects.filter(
            user_profile=user_profile
        ).order_by('-timestamp')

        total_securities_value = 0
        total_cost_basis = 0

        for holding in active_holdings:
            current_stock_price = holding.stock.current_price

            row_market_value = holding.shares_owned * current_stock_price
            row_total_cost = holding.shares_owned * holding.average_buy_price
            row_unrealized_pnl = row_market_value - row_total_cost

            holding.market_value = row_market_value
            holding.unrealized_pnl = row_unrealized_pnl

            total_securities_value += row_market_value
            total_cost_basis += row_total_cost

            available_cash = user_profile.cash_balance
            total_account_net_worth = available_cash + total_securities_value
            total_portfolio_pnl = total_securities_value - total_cost_basis

            context = {
                "profile": user_profile,
                "holdings": active_holdings,
                "transactions": transaction_logs,
                "securities_value": total_securities_value,
                "net_worth": total_account_net_worth,
                "total_pnl": total_portfolio_pnl,
            }

            return render(request, "portfolio.html", context)





















