from django.urls import path
from stock_market.views import MarketDashboardView, TradeFormEndpointView, ExecuteTradeView

urlpatterns = [
    path('market/', MarketDashboardView.as_view(), name='market_dashboard'),
    path('trade/get-form/<str:ticker>/', TradeFormEndpointView.as_view(), name='get_trade_form'),
    path('trade/execute', ExecuteTradeView.as_view(), name='execute_trade'),
]