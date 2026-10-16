from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView

from stock_market.models import Stock


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
