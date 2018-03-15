from django.views.generic import TemplateView, ListView
from sales import models
from django.contrib.auth.mixins import LoginRequiredMixin


class OrdersView(TemplateView):
    template_name = 'sales/orders.html'


class RegionList(LoginRequiredMixin, ListView):
    model = models.Region
    template_name = 'sales/regions/index.html'
