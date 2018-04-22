import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from reports import forms
from core.models import Product
from sales import models


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


@login_required()
def outward_product_summary_report(request, date_0, date_1):
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = datetime.datetime.combine(date_1, datetime.time(23, 59))
    outward = []
    for product in Product.objects.all():
        if not models.OrderProduct.objects. \
                filter(product=product, order__date_delivery__range=(date_0, date_1)).exists():
            break
        total_ordered = models.OrderProduct.objects. \
            filter(product=product, order__date_delivery__range=(date_0, date_1)). \
            aggregate(total=Sum('qty'))
        total_packaged = models.PackageProduct.objects. \
            filter(order_product__product=product,
                   order_product__order__date_delivery__range=(date_0, date_1)). \
            aggregate(total=Sum('qty_weigh'))
        total_customer = models.ReceiptParticular.objects. \
            filter(product=product, receipt__date__range=(date_0_datetime, date_1_datetime)). \
            aggregate(total=Sum('qty'))
        total_cash = models.CashReceiptParticular.objects. \
            filter(product=product, cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
            aggregate(total=Sum('qty'))
        if not total_customer['total']:
            total_customer['total'] = 0
        if not total_cash['total']:
            total_cash['total'] = 0
        total_sale = total_customer['total'] + total_cash['total']
        outward.append({'product': product.name, 'ordered': total_ordered['total'],
                        'packaged': total_packaged['total'],
                        'customer': total_customer['total'],
                        'cash': total_cash['total'],
                        'total_sale': total_sale})
        print(outward)
    return render(request, 'reports/outward-products/report.html',
                  {'outwards': outward})