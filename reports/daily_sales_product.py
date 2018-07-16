import datetime
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import DateField, Sum
from django.db.models.functions import Trunc
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from pytz import timezone as pytz_zone

from reports import forms
from sales import models

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.ProductCustomer(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            product = form.cleaned_data['product']
            return redirect('daily_sales_product_report',
                            date_0=str(date_0), date_1=str(date_1), product=product.id)
    else:
        form = forms.ProductCustomer(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today(), })
    return render(request, 'reports/daily-sales-product/period.html',
                  {'form': form})


def report(request, date_0, date_1, product):
    product = get_object_or_404(models.Product, pk=product)
    period = get_date_period_in_range(date_0, date_1)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime), product=product). \
        annotate(day=Trunc('receipt__date', 'day', output_field=DateField(), )). \
        values('day').annotate(Sum('total'), Sum('qty')).order_by('day')
    sale_bar_graph = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime), product=product). \
        annotate(day=Trunc('receipt__date', period, output_field=DateField(), )). \
        values('day').annotate(Sum('total'), Sum('qty')).order_by('day')
    cash_sales = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime), product=product). \
        annotate(day=Trunc('cash_receipt__date', 'day', output_field=DateField(), )). \
        values('day').annotate(Sum('total'), Sum('qty')).order_by('day')
    cash_sales_bar_graph = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime), product=product). \
        annotate(day=Trunc('cash_receipt__date', period, output_field=DateField(), )). \
        values('day').annotate(Sum('total'), Sum('qty')).order_by('day')
    all_sales_graph = []
    final_sales_graph = []
    for sale in sale_bar_graph:
        all_sales_graph.append({
            'day': sale['day'],
            'customer_amount': sale['total__sum'],
            'customer_qty': sale['qty__sum'],
            'cash_amount': 0,
        })
    for sale in cash_sales_bar_graph:
        all_sales_graph.append({
            'day': sale['day'],
            'customer_amount': 0,
            'cash_amount': sale['total__sum'],
        })
    all_sales_graph.sort(key=lambda x: x['day'])
    for k, v in groupby(all_sales_graph, key=lambda x: x['day']):
        v = list(v)
        final_sales_graph.append({
            'day': k,
            'customer_amount': sum(d['customer_amount'] for d in v),
            'cash_amount': sum(d['cash_amount'] for d in v),
        })
    all_sales = []
    final_sales = []
    for sale in sales:
        all_sales.append({
            'day': sale['day'],
            'customer_amount': sale['total__sum'],
            'customer_qty': sale['qty__sum'],
            'cash_amount': 0,
            'cash_qty': 0
        })
    for sale in cash_sales:
        all_sales.append({
            'day': sale['day'],
            'customer_amount': 0,
            'customer_qty': 0,
            'cash_amount': sale['total__sum'],
            'cash_qty': sale['qty__sum']
        })
    all_sales.sort(key=lambda x: x['day'])
    for k, v in groupby(all_sales, key=lambda x: x['day']):
        v = list(v)
        final_sales.append({
            'day': k,
            'customer_amount': sum(d['customer_amount'] for d in v),
            'customer_qty': sum(d['customer_qty'] for d in v),
            'cash_amount': sum(d['cash_amount'] for d in v),
            'cash_qty': sum(d['cash_qty'] for d in v),
        })
    total_sales = sales.aggregate(Sum('total__sum'), Sum('qty__sum'))
    total_cash_sales = cash_sales.aggregate(Sum('total__sum'), Sum('qty__sum'))
    page = request.GET.get('payed_page', 1)

    paginator = Paginator(final_sales, 10)
    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)
    context_data = {'sales': sales, 'date_0': date_0_datetime, 'date_1': date_1_datetime,
                    'total_sales': total_sales, 'total_cash_sales': total_cash_sales, 'period': period,
                    'product': product, 'sale_bar_graph': final_sales_graph}
    return render(request, 'reports/daily-sales-product/report.html', context_data)


def get_date_period_in_range(date_0, date_1):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    delta = date_1 - date_0
    if delta.days == 30:
        return 'hour'
    if 32 > delta.days > 1:
        return 'day'
    if 365 > delta.days > 33:
        return 'month'
    return 'month'
