import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from core.models import Product, AggregationCenterProduct
from reports import forms
from sales import models


# todo add the right permissions
@login_required()
def outward_product_summary_period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('outward_product_report',
                            date_0=date_0, date_1=date_1)
    else:
        form = forms.SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                              'date_1': datetime.date.today()})
    return render(request, 'reports/outward-products/outward-product-period.html',
                  {'form': form})


# todo add the right permissions
# todo a proposal, let a faster language like go, do the reports and use django to render the data.That should be later
# todo for now, just try to aggregate on writes. Like calculating totals on save of an item and read the main aggregates
@login_required()
def outward_product_summary_report(request, date_0: str, date_1: str):
    """
    :param request:
    :param date_0:
    :param date_1:
    :return:
    """
    str_date_0 = date_0
    str_date_1 = date_1
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = datetime.datetime.combine(date_1, datetime.time(23, 59))
    outward = []
    for product in Product.objects.all():
        if models.OrderProduct.objects. \
                filter(product=product,
                       order__date_delivery__range=(
                       date_0, date_1)).exists() is False and models.PackageProduct.objects. \
                filter(order_product__product=product,
                       order_product__order__date_delivery__range=(
                               date_0, date_1)).exists() is False and models.OrderlessPackage.objects. \
                filter(product=product,
                       date__range=(date_0, date_1)).exists() is False and models.ReceiptParticular.objects. \
                filter(product=product, receipt__date__range=(
                date_0_datetime, date_1_datetime)).exists() is False and models.CashReceiptParticular.objects. \
                filter(product=product, cash_receipt__date__range=(
                date_0_datetime, date_1_datetime)).exists() is False and AggregationCenterProduct.objects.filter(
            product=product,
            date__range=(
                    date_0, date_1)).exists() is False and models.MarketReturn.objects. \
                filter(product=product, date__range=(date_0, date_1)).exists() is False:
            continue
        total_ordered = models.OrderProduct.objects. \
            filter(product=product, order__date_delivery__range=(date_0, date_1)). \
            aggregate(total=Sum('qty'))
        total_packaged = models.PackageProduct.objects. \
            filter(order_product__product=product,
                   order_product__order__date_delivery__range=(date_0, date_1)). \
            aggregate(total=Sum('qty_weigh'))
        total_orderless = models.OrderlessPackage.objects. \
            filter(product=product,
                   date__range=(date_0, date_1)). \
            aggregate(total=Sum('qty'))
        total_customer = models.ReceiptParticular.objects. \
            filter(product=product, receipt__date__range=(date_0_datetime, date_1_datetime)). \
            aggregate(total=Sum('qty'))
        total_cash = models.CashReceiptParticular.objects. \
            filter(product=product, cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
            aggregate(total=Sum('qty'))
        available = AggregationCenterProduct.objects.filter(product=product,
                                                            date__range=(date_0, date_1)). \
            values('aggregation_center__name').annotate(total=Sum('qty'))
        total_available = AggregationCenterProduct.objects.filter(product=product,
                                                                  date__range=(date_0, date_1)). \
            aggregate(total=Sum('qty'))
        if not total_available['total']:
            total_available['total'] = 0
        total_return = models.MarketReturn.objects. \
            filter(product=product, date__range=(date_0, date_1)). \
            aggregate(total=Sum('qty'))
        if not total_return['total']:
            total_return['total'] = 0
        if not total_customer['total']:
            total_customer['total'] = 0
        if not total_cash['total']:
            total_cash['total'] = 0
        if not total_packaged['total']:
            total_packaged['total'] = 0
        if not total_orderless['total']:
            total_orderless['total'] = 0
        total_dispatch = total_packaged['total'] + total_orderless['total']
        total_sale = total_customer['total'] + total_cash['total']
        variance = total_dispatch - total_sale - total_return['total']
        outward.append({'product': product.name, 'ordered': total_ordered['total'],
                        'packaged': total_packaged['total'],
                        'orderless': total_orderless['total'],
                        'total_dispatch': total_dispatch,
                        'customer': total_customer['total'],
                        'cash': total_cash['total'],
                        'total_sale': total_sale,
                        'available': available,
                        'total_available': total_available['total'],
                        'diff': variance,
                        'total_return': total_return['total'],
                        'product_id': product.pk})
    return render(request, 'reports/outward-products/report.html',
                  {'outwards': outward,
                   'date_0': date_0_datetime,
                   'date_1': date_1_datetime,
                   'str_date_0': str_date_0,
                   'str_date_1': str_date_1})
