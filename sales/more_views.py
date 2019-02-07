from datetime import timedelta
from decimal import Decimal

import django_filters
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, F, fields, ExpressionWrapper
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from sales import models
from utils import main_generate_unique_id


class OrderlessFilter(django_filters.FilterSet):
    class Meta:
        model = models.OrderlessPackage
        fields = ('product',)


# todo add the right permissions
@login_required()
@permission_required('sales.view_orderlesspackage')
def orderless_dispatch(request):
    """
    show all orderless dispatch starting with the latest and add a filter bar
    :param request:
    :return:
    """
    yesterday_expression = ExpressionWrapper(F('date') - timedelta(hours=24),
                                            output_field=fields.DateField())
    orderless_list = models.OrderlessPackage.objects.select_related('product'). \
        values('product__name', 'date').annotate(total_qty=Sum('qty'), product_id=F('product__id'),
                                                 yesterday=yesterday_expression).order_by('-date')
    orderless_filter = OrderlessFilter(request.GET, queryset=orderless_list)
    orderless_list = orderless_filter.qs
    paginator = Paginator(orderless_list, 50)
    page = request.GET.get('page', 1)
    try:
        orderless = paginator.page(page)
    except PageNotAnInteger:
        orderless = paginator.page(1)
    except EmptyPage:
        orderless = paginator.page(paginator.num_pages)
    args = {'paginator': paginator, 'filter': orderless_filter,
            'orderless': orderless}
    return render(request, 'sales/orderless/index.html', args)


# todo add the right permissions
@login_required()
@permission_required('sales.view_deposits')
def customer_deposits(request, customer):
    customer = get_object_or_404(models.Customer, pk=customer)
    settle = request.GET.get('settle', None)
    if settle:
        deposits = models.CustomerDeposit.objects.filter(customer=customer,
                                                         remaining_amount__gt=Decimal('0.00'))
    else:
        deposits = models.CustomerDeposit.objects.filter(customer=customer)
    paginator = Paginator(deposits, 50)
    page = request.GET.get('page', 1)
    try:
        deposits = paginator.page(page)
    except PageNotAnInteger:
        deposits = paginator.page(1)
    except EmptyPage:
        deposits = paginator.page(paginator.num_pages)
    return render(request, 'sales/customers/deposits.html', {'paginator': paginator, 'deposits': deposits,
                                                             'customer': customer})


# todo add the right permissions
class AddDeposit(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permissions = ' sales.add_customerdeposit'
    model = models.CustomerDeposit
    fields = ['amount', 'via', 'phone_number', 'transaction_id', 'cheque_number', 'date']
    success_message = 'Deposit added successfully'
    template_name = 'sales/customers/add-deposit.html'

    def get_customer(self):
        customer = get_object_or_404(models.Customer, pk=self.kwargs['customer'])
        return customer

    def get_context_data(self, **kwargs):
        context = super(AddDeposit, self).get_context_data(**kwargs)
        context['customer'] = self.get_customer()
        return context

    def form_valid(self, form):
        deposit = form.save(commit=False)

        deposit.number = main_generate_unique_id()
        deposit.customer = self.get_customer()
        deposit.received_by = self.request.user
        deposit.save()
        return super(AddDeposit, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('customer_deposits', kwargs={'customer': self.kwargs['customer']})


# todo add the right permissions
@login_required()
@permission_required('sales.view_marketreturns')
def market_returns(request):
    returns = models.MarketReturn.objects.select_related('product').values('product__name', 'date', 'type'). \
        order_by('-date').annotate(total_qty=Sum('qty'), product_pk=F('product__id'))
    paginator = Paginator(returns, 50)
    page = request.GET.get('page', 1)
    try:
        returns = paginator.page(page)
    except PageNotAnInteger:
        returns = paginator.page(1)
    except EmptyPage:
        returns = paginator.page(paginator.num_pages)
    return render(request, 'sales/returns/market-returns.html', {'paginator': paginator, 'returns': returns})
