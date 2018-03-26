from datetime import datetime, timedelta

import django_filters
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django_filters import FilterSet
from django_filters.views import FilterView
from django_select2.forms import Select2Widget

from sales import forms
from sales import models
from utils import generate_unique_id


class OrdersView(LoginRequiredMixin, ListView):
    template_name = 'sales/orders/index.html'

    def get_queryset(self):
        return models.Order.objects.select_related('customer', 'received_by').values('number', 'customer__shop_name',
                                                                                     'received_by__username',
                                                                                     'date_delivery',
                                                                                     'created_at').all()


class RegionList(LoginRequiredMixin, ListView):
    model = models.Region
    template_name = 'sales/regions/index.html'


@login_required()
def create_regions(request):
    region_formset = modelformset_factory(models.Region, fields=('name',), max_num=5, min_num=1)
    if request.method == 'POST':
        formset = region_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'regions added successfully!')
            return redirect(reverse_lazy('regions'))
    else:
        formset = region_formset(queryset=models.Region.objects.none())
    return render(request, 'sales/regions/create.html', {'formset': formset})


class UpdateRegion(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = models.Region
    fields = ['name']
    template_name = 'sales/regions/update.html'
    success_url = reverse_lazy('regions')
    success_message = 'region updated successfully'


class DeleteRegion(LoginRequiredMixin, DeleteView):
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
    date = django_filters.DateFromToRangeFilter(name='date',
                                                label='Date (Between)')

    class Meta:
        model = models.ReceiptParticular
        fields = ('date',)


class SalesList(LoginRequiredMixin, FilterView):
    model = models.Receipt
    template_name = 'sales/sales/index.html'
    filterset_class = SalesFilterSet

    def get_queryset(self):
        return models.Receipt.objects.all().select_related('customer',
                                                           'served_by')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(SalesList, self).get_context_data(object_list=None, **kwargs)
        date_30_days_ago = datetime.now() - timedelta(days=30)
        date_30_days_ago = date_30_days_ago.strftime("%Y-%m-%d")
        data['date_30_days_ago'] = date_30_days_ago
        return data


@login_required()
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


class DeleteCustomer(LoginRequiredMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Customer removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'sales/regions/delete.html'
    model = models.Customer
    success_url = reverse_lazy('customers')


class UpdateCustomer(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = models.Customer
    fields = ['shop_name', 'nick_name', 'location', 'phone_number', 'region']
    template_name = 'sales/customers/update.html'
    success_url = reverse_lazy('customers')
    success_message = 'Customer updated successfully'


@login_required()
def add_prices(request, pk):
    prices_formset = modelformset_factory(models.CustomerPrice, fields=('product', 'price'),
                                          widgets={'product': Select2Widget}, extra=5, min_num=1,
                                          can_delete=True)
    customer = models.Customer.objects.get(pk=pk)
    if request.method == 'POST':
        formset = prices_formset(request.POST)
        if formset.is_valid():
            prices = formset.save(commit=False)
            for price in prices:
                price.customer = customer
                price.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, 'price added successfully!')
            return redirect(reverse_lazy('customers'))
    else:
        formset = prices_formset(queryset=models.CustomerPrice.objects.select_related('product').filter(customer=pk))
    return render(request, 'crud/formset-create.html', {'formset': formset,
                                                        "customer": customer,
                                                        'create_name': customer.shop_name + ' Prices',
                                                        'create_sub_name': 'Price'})


@login_required()
def add_discounts(request, pk):
    discounts_formset = modelformset_factory(models.CustomerDiscount, fields=('product', 'discount'),
                                             widgets={'product': Select2Widget}, extra=10,
                                             can_delete=True)
    customer = models.Customer.objects.get(pk=pk)
    if request.method == 'POST':
        formset = discounts_formset(request.POST)
        if formset.is_valid():
            discounts = formset.save(commit=False)
            for discount in discounts:
                discount.customer = customer
                discount.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, 'discounts added successfully!')
            return redirect(reverse_lazy('customers'))
    else:
        formset = discounts_formset(
            queryset=models.CustomerDiscount.objects.select_related('product').filter(customer=pk))
    return render(request, 'crud/formset-create.html', {'formset': formset,
                                                        "customer": customer,
                                                        'create_name': customer.shop_name + ' Discounts',
                                                        'create_sub_name': 'discount'})


@login_required()
def place_order(request, pk):
    orders_formset = modelformset_factory(models.OrderProduct,
                                          fields=('product', 'qty', 'price', 'discount'),
                                          widgets={'product': Select2Widget,
                                                   'price': Select2Widget,
                                                   'discount': Select2Widget}, min_num=1,
                                          extra=10,
                                          can_delete=True)
    customer = models.Customer.objects.get(pk=pk)
    if request.method == 'POST':
        formset = orders_formset(request.POST)
        for form in formset:
            form.fields['price'].queryset = models.CustomerPrice.objects.filter(customer=customer)
            form.fields['discount'].queryset = models.CustomerDiscount.objects.filter(customer=customer)
        main_order = models.Order()
        main_order.number = generate_unique_id(request.user.id)
        main_order.received_by = request.user
        main_order.customer = customer
        if formset.is_valid():
            main_order.save()
            orders = formset.save(commit=False)
            for order in orders:
                order.number = generate_unique_id(request.user.id)
                order.order = main_order
                order.save()
                distribution_point = models.OrderDistributionPoint()
                distribution_point.order_product = order
                distribution_point.qty = order.qty
                distribution_point.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, 'orders added successfully!')
            return redirect(reverse_lazy('customers'))
    else:
        formset = orders_formset(
            queryset=models.OrderProduct.objects.none())
        for form in formset:
            form.fields['price'].queryset = models.CustomerPrice.objects.filter(customer=customer)
            form.fields['discount'].queryset = models.CustomerDiscount.objects.filter(customer=customer)
    return render(request, 'crud/formset-create.html', {'formset': formset,
                                                        "customer": customer,
                                                        'create_name': customer.shop_name + ' Orders',
                                                        'create_sub_name': 'item'})


@login_required()
def update_order(request, pk):
    orders_formset = modelformset_factory(models.OrderProduct,
                                          fields=('product', 'qty', 'price', 'discount'),
                                          widgets={'product': Select2Widget,
                                                   'price': Select2Widget,
                                                   'discount': Select2Widget}, extra=3,
                                          can_delete=True,
                                          min_num=1)
    order = models.Order.objects.get(pk=pk)
    if request.method == 'POST':
        formset = orders_formset(request.POST)
        for form in formset:
            form.fields['price'].queryset = models.CustomerPrice.objects.filter(customer=order.customer)
            form.fields['discount'].queryset = models.CustomerDiscount.objects.filter(customer=order.customer)
        if formset.is_valid():
            items = formset.save(commit=False)
            for item in items:
                item.order = order
                item.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, 'orders updated successfully!')
            return redirect(reverse_lazy('orders'))
    else:
        formset = orders_formset(
            queryset=models.OrderProduct.objects.filter(order=order))
        for form in formset:
            form.fields['price'].queryset = models.CustomerPrice.objects.filter(customer=order.customer)
            form.fields['discount'].queryset = models.CustomerDiscount.objects.filter(customer=order.customer)
    return render(request, 'crud/formset-create.html', {'formset': formset,
                                                        'create_name': 'Update order ' + order.number + ' for ' + order.customer.shop_name,
                                                        'create_sub_name': 'order'})


class DeleteOrder(LoginRequiredMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Order removed!')
        return super().post(request, *args, **kwargs)

    template_name = 'crud/delete.html'
    model = models.Order
    success_url = reverse_lazy('orders')


@login_required()
def order_detail(request, pk):
    order = get_object_or_404(models.Order, pk=pk)
    return render(request, 'sales/orders/order-detail.html', {'order': order})


class CashSalesFilterSet(FilterSet):
    date = django_filters.DateFromToRangeFilter(name='receipt__date',
                                                label='Date (Between)')

    class Meta:
        model = models.CashReceiptParticular
        fields = ('date',)


class CashSalesList(LoginRequiredMixin, FilterView):
    model = models.CashReceiptParticular
    template_name = 'sales/sales/cash-sale.html'
    filterset_class = CashSalesFilterSet

    def get_queryset(self):
        return models.CashReceiptParticular.objects.all().select_related('cash_receipt',
                                                                         'product')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(CashSalesList, self).get_context_data(object_list=None, **kwargs)
        date_30_days_ago = datetime.now() - timedelta(days=30)
        date_30_days_ago = date_30_days_ago.strftime("%Y-%m-%d")
        data['date_30_days_ago'] = date_30_days_ago
        return data


@login_required()
def order_distribution_list(request):
    points_formset = modelformset_factory(models.OrderDistributionPoint,
                                          fields=('center', 'qty'),
                                          widgets={'center': Select2Widget}, extra=1,
                                          can_delete=True,
                                          min_num=1)
    form = forms.ProductSelectionForm()
    order_products = models.OrderProduct.objects.none()
    formset = points_formset(
        queryset=models.OrderDistributionPoint.objects.none())
    if request.method == 'POST':
        formset = points_formset(request.POST)
        order_product = request.POST.get("order_product")
        url = request.POST.get("url")
        order_product = models.OrderProduct.objects.get(pk=order_product)
        if formset.is_valid():
            points = formset.save(commit=False)
            for point in points:
                point.order_product = order_product
                point.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, 'orders distributed successfully!')
            return redirect(url)
    else:
        form = forms.ProductSelectionForm(request.GET)
        if form.is_valid():
            product = form.cleaned_data['product']
            order_products = models.OrderProduct.objects.select_related(
                'order__customer', 'order', 'product').filter(product=product)
            formset = points_formset(
                queryset=models.OrderDistributionPoint.objects.filter(order_product__product=product))
    return render(request, 'sales/orders/order-distribution-form.html', {'form': form,
                                                                         'order_products': order_products,
                                                                         'formset': formset
                                                                         })
