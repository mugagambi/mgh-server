import datetime
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.shortcuts import redirect, render

from core.models import Product
from reports import forms
from sales import models


@login_required()
def outward_stock_summary_period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('outward_stock_report',
                            date_0=date_0, date_1=date_1)
    else:
        form = forms.SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                              'date_1': datetime.date.today()})
    return render(request, 'reports/outward-stock/outward-stock-period.html',
                  {'form': form})


# todo add the required permissions
# todo read the pre-aggregated data for each product
@login_required()
def outward_stock_summary_report(request, date_0, date_1):
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = datetime.datetime.combine(date_1, datetime.time(23, 59))
    outward = []
    for product in Product.objects.all():
        total_customer_qty = models.ReceiptParticular.objects.filter(product=product,
                                                                     receipt__date__range=(date_0_datetime,
                                                                                           date_1_datetime)). \
            aggregate(total=Sum('qty'))
        total_cash_qty = models.CashReceiptParticular.objects.filter(product=product,
                                                                     cash_receipt__date__range=(date_0_datetime,
                                                                                                date_1_datetime)). \
            aggregate(total=Sum('qty'))
        if not total_customer_qty['total'] and not total_cash_qty['total']:
            continue
        total_customer_value = models.ReceiptParticular.objects.filter(
            product=product, receipt__date__range=(date_0_datetime, date_1_datetime)
        ).aggregate(total=Sum(F('qty') * F('price')))
        total_cash_value = models.CashReceiptParticular.objects.filter(
            product=product, cash_receipt__date__range=(date_0_datetime, date_1_datetime)
        ).aggregate(total=Sum(F('qty') * F('price')))
        if not total_customer_qty['total']:
            total_customer_price_avg = 0
        else:
            total_customer_price_avg = total_customer_value['total'] / total_customer_qty['total']
        if not total_cash_qty['total']:
            total_cash_price_avg = 0
        else:
            total_cash_price_avg = total_cash_value['total'] / total_cash_qty['total']
        if not total_customer_qty['total']:
            total_customer_qty = {'total': 0}
        if not total_cash_qty['total']:
            total_cash_qty = {'total': 0}
        total_sale_qty = total_customer_qty['total'] + total_cash_qty['total']
        if not total_customer_value['total']:
            total_customer_value = {'total': 0}
        if not total_cash_value['total']:
            total_cash_value = {'total': 0}
        total_sale_value = total_customer_value['total'] + total_cash_value['total']
        total_sale_price_average = total_sale_value / total_sale_qty
        outward.append({'product': product.name, 'total_customer_qty': total_customer_qty['total'],
                        'total_cash_qty': total_cash_qty['total'],
                        'total_customer_value': total_customer_value['total'],
                        'total_cash_value': total_cash_value['total'],
                        'total_customer_price_avg': total_customer_price_avg,
                        'total_cash_price_avg': total_cash_price_avg,
                        'total_sale_qty': total_sale_qty,
                        'total_sale_value': total_sale_value,
                        'total_sale_price_average': total_sale_price_average})
    grand_customer_value = reduce(lambda a, b: a + b['total_customer_value'], outward, 0)
    grand_cash_value = reduce(lambda a, b: a + b['total_cash_value'], outward, 0)
    total_grand_value = reduce(lambda a, b: a + b['total_sale_value'], outward, 0)
    return render(request, 'reports/outward-stock/report.html',
                  {'outwards': outward,
                   'grand_customer_value': grand_customer_value,
                   'grand_cash_value': grand_cash_value,
                   'total_grand_value': total_grand_value,
                   'date_0': date_0_datetime,
                   'date_1': date_1_datetime})
