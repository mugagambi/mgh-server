import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render, get_object_or_404

from reports import forms
from core.models import Product, AggregationCenterProduct
from sales import models


@login_required()
def outward_product_customer_summary_period(request):
    if request.method == 'POST':
        form = forms.ProductCustomer(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            product = form.cleaned_data['product']
            return redirect('outward-product-per-customer',
                            date_0=date_0, date_1=date_1, product_id=product.id)
    else:
        form = forms.ProductCustomer(initial={'date_0': datetime.date.today(),
                                              'date_1': datetime.date.today()})
    return render(request, 'reports/outward-product-customer/date-period.html',
                  {'form': form})


def items_exist(customer, product_id, date_0, date_1, datetime_0, datetime_1):
    if models.OrderProduct.objects.filter(product__id=product_id, order__date_delivery__range=(date_0, date_1),
                                          order__customer__id=customer).exists():
        return True
    if models.PackageProduct.objects.filter(order_product__product=product_id,
                                            order_product__order__date_delivery__range=(
                                                    date_0, date_1),
                                            order_product__order__customer__id=customer).exists():
        return True
    if models.ReceiptParticular.objects.filter(product__id=product_id,
                                               receipt__customer__id=customer,
                                               receipt__date__range=(
                                                       datetime_0, datetime_1)).exists():
        return True
    if models.Return.objects.filter(product__id=product_id,
                                    customer__id=customer, date__range=(datetime_0, datetime_1)).exists():
        return True
    return False


@login_required()
def outward_product_summary_report(request, date_0, date_1, product_id):
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = datetime.datetime.combine(date_1, datetime.time(23, 59))
    product = get_object_or_404(Product, pk=product_id)
    outward = []
    qs = models.Customer.objects.all()
    for customer in qs:
        if not models.OrderProduct.objects.filter(product=product,
                                                  order__date_delivery__range=(date_0, date_1),
                                                  order__customer=customer).exists():
            if not models.ReceiptParticular.objects.filter(product=product, receipt__customer=customer,
                                                           receipt__date__range=(date_0_datetime,
                                                                                 date_1_datetime)).exists():
                if not models.Return.objects.filter(product=product, customer=customer,
                                                    date__range=(date_0_datetime, date_1_datetime)).exists():
                    continue
        total_ordered = models.OrderProduct.objects.filter(product=product,
                                                           order__date_delivery__range=(date_0, date_1),
                                                           order__customer=customer).aggregate(total=Sum('qty'))
        if not total_ordered['total']:
            total_ordered['total'] = 0
        total_packaged = models.PackageProduct.objects.filter(order_product__product=product,
                                                              order_product__order__customer=customer,
                                                              order_product__order__date_delivery__range=(
                                                                  date_0, date_1)).aggregate(total=Sum('qty_weigh'))
        if not total_packaged['total']:
            total_packaged['total'] = 0
        total_sold = models.ReceiptParticular.objects.filter(product=product,
                                                             receipt__customer=customer,
                                                             receipt__date__range=(date_0_datetime, date_1_datetime)). \
            aggregate(total=Sum('qty'))
        if not total_sold['total']:
            total_sold['total'] = 0
        total_return = models.Return.objects.filter(product=product, customer=customer,
                                                    date__range=(date_0_datetime, date_1_datetime)).aggregate(
            total=Sum('qty'))
        if not total_return['total']:
            total_return['total'] = 0
        total_out = total_return['total'] + total_sold['total']
        variance = total_packaged['total'] - total_out
        outward.append({'customer': customer, 'ordered': total_ordered['total'],
                        'packaged': total_packaged['total'],
                        'total_sold': total_sold['total'],
                        'total_return': total_return['total'],
                        'variance': variance})
    total_ordered = models.OrderProduct.objects.filter(product=product,
                                                       order__date_delivery__range=(date_0, date_1)).aggregate(
        total=Sum('qty'))
    if not total_ordered['total']:
        total_ordered['total'] = 0
    total_packaged = models.PackageProduct.objects.filter(order_product__product=product,
                                                          order_product__order__date_delivery__range=(
                                                              date_0, date_1)).aggregate(total=Sum('qty_weigh'))
    total_sold = models.ReceiptParticular.objects.filter(product=product,
                                                         receipt__date__range=(
                                                             date_0_datetime, date_1_datetime)).aggregate(
        total=Sum('qty'))
    total_return = models.Return.objects.filter(product=product,
                                                date__range=(date_0_datetime, date_1_datetime)).aggregate(
        total=Sum('qty'))
    if not total_return['total']:
        total_return['total'] = 0
    total_out = total_return['total'] + total_sold['total']
    variance = total_out - total_packaged['total']
    return render(request, 'reports/outward-product-customer/report.html',
                  {'outwards': outward,
                   'date_0': date_0_datetime,
                   'date_1': date_1_datetime,
                   'product': product,
                   'total_ordered': total_ordered['total'],
                   'total_packaged': total_packaged['total'],
                   'total_sold': total_sold['total'],
                   'total_return': total_return['total'],
                   'variance': variance})
