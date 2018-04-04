from datetime import datetime, timedelta

import django_filters
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum
from django.forms import modelformset_factory
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django_filters import FilterSet
from django_filters.views import FilterView
from django_select2.forms import Select2Widget

from sales import forms
from sales import models
from system_settings.models import Settings
from utils import generate_unique_id


class OrdersFilter(FilterSet):
    date_delivery_between = django_filters.DateTimeFromToRangeFilter(name='date_delivery',
                                                                     label='Date of Delivery (Between)')
    created_at_between = django_filters.DateTimeFromToRangeFilter(name='created_at',
                                                                  label='Created at (Between)')
    number = django_filters.CharFilter(lookup_expr='icontains', name='number', label='Order Number')

    class Meta:
        model = models.Order
        fields = (
            'number', 'customer', 'received_by', 'date_delivery', 'created_at', 'date_delivery_between',
            'created_at_between')


@login_required()
def order_list(request):
    order_list = models.Order.objects.select_related('customer', 'received_by').values('number', 'customer__shop_name',
                                                                                       'received_by__username',
                                                                                       'date_delivery',
                                                                                       'created_at').all()
    order_filter = OrdersFilter(request.GET, queryset=order_list)
    order_list = order_filter.qs
    paginator = Paginator(order_list, 50)
    page = request.GET.get('page', 1)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    print(order_filter)
    args = {'paginator': paginator, 'filter': order_filter,
            'orders': orders, }
    return render(request, 'sales/orders/index.html', args)


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


class CustomerFilter(FilterSet):
    class Meta:
        model = models.Customer
        fields = ('region', 'added_by')


@login_required()
def customer_list(request):
    if request.method == 'POST':
        form = forms.PlaceOrderModal(request.POST)
        if form.is_valid():
            customer_number = form.cleaned_data['customer_number']
            date = form.cleaned_data['date_of_delivery']
            return redirect('place-order', pk=customer_number, date=date)
    else:
        form = forms.PlaceOrderModal(initial={'date_of_delivery': datetime.now() + timedelta(days=1),
                                              'customer_number': ''})
    f = CustomerFilter(request.GET, queryset=models.Customer.objects.all())
    return render(request, 'sales/customers/index.html', {'filter': f, 'form': form})


class SalesFilterSet(FilterSet):
    date_between = django_filters.DateFromToRangeFilter(name='date',
                                                        label='Date (Between)')
    number = django_filters.CharFilter(lookup_expr='icontains',
                                       label='Receipt Number',
                                       name='number')

    class Meta:
        model = models.Receipt
        fields = ('number', 'customer', 'served_by', 'date', 'date_between')


@login_required()
def sales_list(request):
    sale_list = models.Receipt.objects.select_related('customer',
                                                      'served_by').filter(
        receiptpayment__amount__isnull=False).annotate(
        total_qty=Sum('receiptparticular__qty'),
        total_amount=Sum('receiptparticular__total'))
    sale_filter = SalesFilterSet(request.GET, queryset=sale_list)
    sale_list = sale_filter.qs
    paginator = Paginator(sale_list, 50)
    page = request.GET.get('page', 1)
    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)
    print(sale_filter)
    args = {'paginator': paginator, 'filter': sale_filter,
            'sales': sales, }
    return render(request, 'sales/sales/index.html', args)


@login_required()
def receipt_detail(request, pk):
    try:
        receipt = models.Receipt.objects.select_related('customer', 'served_by').get(pk=pk)
    except models.Receipt.DoesNotExist:
        raise Http404('Receipt not found')
    particulars = models.ReceiptParticular.objects.select_related('product').filter(receipt=receipt)
    orderlessparticulars = models.OrderlessParticular.objects.select_related('product').filter(receipt=receipt)
    payments = models.ReceiptPayment.objects.filter(receipt=receipt)
    particulars_qty = particulars.aggregate(sum=Sum('qty'))
    orderless_qty = orderlessparticulars.aggregate(sum=Sum('qty'))
    total_qty = particulars_qty['sum'] + orderless_qty['sum']
    particulars_amount = particulars.aggregate(sum=Sum('total'))
    orderless_amount = particulars.aggregate(sum=Sum('total'))
    total_amount = particulars_amount['sum'] + orderless_amount['sum']
    total_payed_amount = payments.aggregate(sum=Sum('amount'))
    balance = total_payed_amount['sum'] - total_amount
    return render(request, 'sales/sales/receipt.html', {'receipt': receipt,
                                                        'particulars': particulars,
                                                        'total_qty': total_qty,
                                                        'total_amount': total_amount,
                                                        'payments': payments,
                                                        'total_payment': total_payed_amount,
                                                        'balance': balance,
                                                        'orderlessparticulars': orderlessparticulars
                                                        })


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

    template_name = 'crud/delete.html'
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
        formset = prices_formset(
            queryset=models.CustomerPrice.objects.select_related('product').filter(customer=pk))
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
def place_order(request, pk, date):
    settings = Settings.objects.all().first()
    if not settings:
        Settings.objects.create()
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
        main_order.date_delivery = date
        if formset.is_valid():
            if not settings.main_distribution:
                messages.success(request, 'You need to have a main center')
                return redirect(reverse_lazy('main-center'))
            orders = formset.save(commit=False)
            for order in orders:
                if order.price.product != order.product:
                    messages.error(request,
                                   '%s price expected. Found %s price.Kindly correct the error on the form below' % (
                                       order.product, order.price.product))
                    return render(request, 'sales/customers/place-order.html', {'formset': formset,
                                                                                "customer": customer,
                                                                                'create_name': customer.shop_name + ' Orders',
                                                                                'create_sub_name': 'item'})
                main_order.save()
                order.number = generate_unique_id(request.user.id)
                order.order = main_order
                order.save()
                distribution_point = models.OrderDistributionPoint()
                distribution_point.order_product = order
                distribution_point.qty = order.qty
                distribution_point.center = settings.main_distribution
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
    return render(request, 'sales/customers/place-order.html', {'formset': formset,
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
