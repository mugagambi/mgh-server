from datetime import datetime, timedelta

import django_filters
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import UpdateView, DeleteView
from django_filters import FilterSet
from django_filters.views import FilterView
from django_select2.forms import Select2Widget
from sales import forms

from sales import models
from utils import generate_unique_id


class OrdersView(TemplateView):
    template_name = 'sales/orders.html'


class RegionList(LoginRequiredMixin, ListView):
    model = models.Region
    template_name = 'sales/regions/index.html'


def create_regions(request):
    region_formset = modelformset_factory(models.Region, fields=('name',), max_num=10)
    if request.method == 'POST':
        formset = region_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'regions added successfully!')
            return redirect(reverse_lazy('regions'))
    else:
        formset = region_formset(queryset=models.Region.objects.none())
        return render(request, 'sales/regions/create.html', {'formset': formset})


class UpdateRegion(SuccessMessageMixin, UpdateView):
    model = models.Region
    fields = ['name']
    template_name = 'sales/regions/update.html'
    success_url = reverse_lazy('regions')
    success_message = 'region updated successfully'


class DeleteRegion(DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'region removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'sales/regions/delete.html'
    model = models.Region
    success_url = reverse_lazy('regions')


class CustomerList(LoginRequiredMixin, FilterView):
    model = models.Customer
    template_name = 'sales/customers/index.html'
    filter_fields = ('region', 'added_by')


class SalesFilterSet(FilterSet):
    date = django_filters.DateFromToRangeFilter(name='receipt__date',
                                                label='Date (Between)')

    class Meta:
        model = models.ReceiptParticular
        fields = ('date',)


class SalesList(LoginRequiredMixin, FilterView):
    model = models.ReceiptParticular
    template_name = 'sales/sales/index.html'
    filterset_class = SalesFilterSet

    def get_queryset(self):
        return models.ReceiptParticular.objects.all().select_related('receipt',
                                                                     'package_product__order_product__product',
                                                                     'receipt__customer')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(SalesList, self).get_context_data(object_list=None, **kwargs)
        date_30_days_ago = datetime.now() - timedelta(days=30)
        date_30_days_ago = date_30_days_ago.strftime("%Y-%m-%d")
        data['date_30_days_ago'] = date_30_days_ago
        return data


def create_customer(request):
    if request.method == 'POST':
        form = forms.CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.number = generate_unique_id(request.user.id)
            customer.added_by = request.user
            customer.save()
            messages.success(request, 'Customer added successfully')
            return redirect('customers')
    else:
        form = forms.CustomerForm()
        return render(request, 'sales/customers/create.html', {'form': form})


class DeleteCustomer(DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Customer removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'sales/regions/delete.html'
    model = models.Customer
    success_url = reverse_lazy('customers')


class UpdateCustomer(SuccessMessageMixin, UpdateView):
    model = models.Customer
    fields = ['shop_name', 'nick_name', 'location', 'phone_number', 'region']
    template_name = 'sales/customers/update.html'
    success_url = reverse_lazy('customers')
    success_message = 'Customer updated successfully'


def add_prices(request, pk):
    prices_formset = modelformset_factory(models.CustomerPrice, fields=('price', 'product'),
                                          widgets={'product': Select2Widget}, max_num=10)
    customer = models.Customer.objects.get(pk=pk)
    if request.method == 'POST':
        formset = prices_formset(request.POST)
        if formset.is_valid():
            prices = formset.save(commit=False)
            for price in prices:
                price.customer = customer
                price.save()
            messages.success(request, 'regions added successfully!')
            return redirect(reverse_lazy('customers'))
    else:
        formset = prices_formset(queryset=models.CustomerPrice.objects.select_related('product').filter(customer=pk))
    return render(request, 'sales/customers/add-prices.html', {'formset': formset,
                                                               "customer": customer})
