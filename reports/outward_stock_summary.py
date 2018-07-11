import datetime
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from pytz import timezone as pytz_zone

from reports import forms
from sales import models

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


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


@login_required()
def outward_stock_summary_alt__report(request, date_0, date_1):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    customer = models.ReceiptParticular.objects.filter(receipt__date__range=(date_0_datetime, date_1_datetime)). \
        values('product__name').annotate(qty=Sum('qty'), total=Sum('total'))
    cash = models.CashReceiptParticular.objects.filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
        values('product__name').annotate(qty=Sum('qty'), total=Sum('total'))
    all_sales = []
    for sale in customer:
        all_sales.append({
            'product': sale['product__name'],
            'total_customer_qty': sale['qty'],
            'total_customer_value': sale['total'],
            'total_customer_price_avg': sale['total' or 0] / sale['qty' or 0],
            'total_cash_qty': 0,
            'total_cash_value': 0,
            'total_cash_price_avg': 0
        })
    for sale in cash:
        all_sales.append({
            'product': sale['product__name'],
            'total_customer_qty': 0,
            'total_customer_value': 0,
            'total_customer_price_avg': 0,
            'total_cash_qty': sale['qty'],
            'total_cash_value': sale['total'],
            'total_cash_price_avg': sale['total' or 0] / sale['qty' or 0]
        })
    all_sales.sort(key=lambda x: x['product'])
    outward = []
    for k, v in groupby(all_sales, key=lambda x: x['product']):
        v = list(v)
        obj = {
            'product': k,
            'total_customer_qty': sum(d['total_customer_qty'] for d in v),
            'total_customer_value': sum(d['total_customer_value'] for d in v),
            'total_customer_price_avg': sum(d['total_customer_price_avg'] for d in v),
            'total_cash_qty': sum(d['total_cash_qty'] for d in v),
            'total_cash_value': sum(d['total_cash_value'] for d in v),
            'total_cash_price_avg': sum(d['total_cash_price_avg'] for d in v),
        }
        if obj['total_customer_qty'] != 0 and obj['total_cash_qty'] != 0:
            value = obj['total_customer_value'] + obj['total_cash_value']
            qty = obj['total_customer_qty'] + obj['total_cash_qty']
            obj['total_sale_avg'] = value / qty
        outward.append(obj)
    customer_value = customer.aggregate(Sum('total'))
    cash_value = cash.aggregate(Sum('total'))
    grand_customer_value = customer_value['total__sum']
    grand_cash_value = cash_value['total__sum']
    if not grand_customer_value and not grand_cash_value:
        total_grand_value = None
    elif not grand_customer_value:
        total_grand_value = grand_cash_value
    elif not grand_cash_value:
        total_grand_value = grand_customer_value
    else:
        total_grand_value = grand_customer_value + grand_cash_value
    return render(request, 'reports/outward-stock/report.html',
                  {'outwards': outward,
                   'grand_customer_value': grand_customer_value,
                   'grand_cash_value': grand_cash_value,
                   'total_grand_value': total_grand_value,
                   'date_0': date_0_datetime,
                   'date_1': date_1_datetime})
