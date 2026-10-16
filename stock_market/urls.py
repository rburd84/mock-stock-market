from django.urls import path
from stock_market.views import MarketDashboardView

urlpatterns = [
    path('market/', MarketDashboardView.as_view(), name='market_dashboard'),
]