from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, AccessMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.utils.dateparse import parse_date
from django.views.generic import CreateView
from rest_framework.reverse import reverse_lazy

from core.models import Product
from sales.forms import OrderlessDispatchUpdateForm
from utils import main_generate_unique_id
from .models import MarketReturn


class CreateOrderlessDispatch(LoginRequiredMixin, PermissionRequiredMixin, AccessMixin, SuccessMessageMixin,
                              CreateView):
    model = MarketReturn
    permission_required = 'sales.add_marketreturn'
    permission_denied_message = 'You do not have permission to perform this task.'
    fields = ['product', 'qty', 'date', 'type']
    success_url = reverse_lazy('market_returns')
    success_message = 'Returns added successfully added'
    template_name = 'sales/returns/create_market_return.html'


@login_required()
@permission_required('sales.change_marketreturn')
def update_market_return(request):
    product_id = request.GET.get('product_id', None)
    if not product_id:
        messages.error(request, 'You need to provide the product')
        return redirect(request.META.get('HTTP_REFERER'))
    date = request.GET.get('date', None)
    if not date:
        messages.error(request, 'You need to provide the date')
        return redirect(request.META.get('HTTP_REFERER'))
    state = request.GET.get('state', None)
    if not state:
        messages.error(request, 'You need to provide if Salvageable or UnSalvageable')
        return redirect(request.META.get('HTTP_REFERER'))
    old_qty = request.GET.get('old_qty', None)
    if not old_qty:
        messages.error(request, 'You need to provide the previous qty')
        return redirect(request.META.get('HTTP_REFERER'))
    product = get_object_or_404(Product, pk=product_id)
    date = parse_date(date)
    if request.method == 'POST':
        form = OrderlessDispatchUpdateForm(request.POST)
        if form.is_valid():
            diff = form.cleaned_data['new_qty'] - Decimal(old_qty)
            MarketReturn.objects.create(product=product, date=date, qty=diff, number=main_generate_unique_id(),
                                        type=state)
            messages.success(request, 'market return updated successfully')
            return redirect('market_returns')
    form = OrderlessDispatchUpdateForm(initial={'new_qty': old_qty})
    return render(request, 'sales/returns/create_market_return.html',
                  {'object': product, 'date': date, 'form': form, 'state': state})
