from django.urls import path
from django.contrib.auth import views as auth_views

from stock_market.views import (
    MarketDashboardView,
    TradeFormEndpointView,
    ExecuteTradeView,
    StockDetailView,
    UserPortfolioView,
    UserSignUpView
)

urlpatterns = [
    path('market/', MarketDashboardView.as_view(), name='market_dashboard'),
    path('trade/get-form/<str:ticker>/', TradeFormEndpointView.as_view(), name='get_trade_form'),
    path('trade/execute', ExecuteTradeView.as_view(), name='execute_trade'),
    path('stock/<str:ticker>/', StockDetailView.as_view(), name='stock_detail'),
    path('portfolio/', UserPortfolioView.as_view(), name='user_portfolio'),
    path('accounts/signup/', UserSignUpView.as_view(), name='signup'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
