from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, AccessMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.dateparse import parse_date
from django.views.generic import CreateView
from rest_framework.reverse import reverse_lazy

from core.models import Product
from sales.forms import OrderlessDispatchUpdateForm
from utils import main_generate_unique_id
from .models import OrderlessPackage


class CreateOrderlessDispatch(LoginRequiredMixin, PermissionRequiredMixin, AccessMixin, SuccessMessageMixin,
                              CreateView):
    model = OrderlessPackage
    permission_required = 'sales.add_orderlesspackage'
    permission_denied_message = 'You do not have permission to perform this task.'
    fields = ['product', 'qty', 'date']
    success_url = reverse_lazy('orderless_dispatch')
    success_message = 'orderless package successfully added'
    template_name = 'sales/orderless/create.html'


@login_required()
@permission_required('sales.change_orderlesspackage')
def update_orderless_dispatch(request):
    product_id = request.GET.get('product_id', None)
    if not product_id:
        messages.error(request, 'You need to provide the product')
        return redirect(request.META.get('HTTP_REFERER'))
    date = request.GET.get('date', None)
    if not date:
        messages.error(request, 'You need to provide the date')
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
            OrderlessPackage.objects.create(product=product, date=date, qty=diff, number=main_generate_unique_id())
            messages.success(request, 'package updated successfully')
            return redirect('orderless_dispatch')
    form = OrderlessDispatchUpdateForm(initial={'new_qty': old_qty})
    return render(request, 'sales/orderless/create.html', {'object': product, 'date': date, 'form': form})


@login_required()
@permission_required('sales.delete_orderlesspackage')
def remove_orderless_dispatch(request):
    product_id = request.GET.get('product_id', None)
    if not product_id:
        messages.error(request, 'You need to provide the product')
        return redirect(request.META.get('HTTP_REFERER'))
    date = request.GET.get('date', None)
    if not date:
        messages.error(request, 'You need to provide the date')
        return redirect(request.META.get('HTTP_REFERER'))
    product = get_object_or_404(Product, pk=product_id)
    date = parse_date(date)
    OrderlessPackage.objects.select_related('product').filter(product=product, date=date).delete()
    messages.success(request, 'package removed successfully')
    return redirect('orderless_dispatch')
