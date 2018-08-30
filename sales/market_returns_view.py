from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, AccessMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
from rest_framework.reverse import reverse_lazy

from .models import MarketReturn


class CreateOrderlessDispatch(LoginRequiredMixin, PermissionRequiredMixin, AccessMixin, SuccessMessageMixin,
                              CreateView):
    model = MarketReturn
    permission_required = 'sales.add_marketreturn'
    permission_denied_message = 'You do not have permission to perform this task.'
    fields = ['product', 'qty', 'date', 'type']
    success_url = reverse_lazy('market_returns')
    success_message = 'Returns added successfully added'
    template_name = 'sales/orderless/create.html'
