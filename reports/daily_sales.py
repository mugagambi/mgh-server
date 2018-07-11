import datetime
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import DateField, Sum
from django.db.models.functions import Trunc
from django.shortcuts import redirect, render
from django.utils import timezone
from pytz import timezone as pytz_zone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from reports import forms
from sales import models
from .serializers import CustomDailySalesChartSerializer

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('daily_sales_report',
                            date_0=str(date_0), date_1=str(date_1))
    else:
        form = forms.SaleSummaryDate(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today(), })
    return render(request, 'reports/daily_sales/period.html',
                  {'form': form})


def report(request, date_0, date_1):
    period = get_date_period_in_range(date_0, date_1)
    date_0_str = date_0
    date_1_str = date_1
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    sales_values = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('receipt__date', 'day', output_field=DateField(), )). \
        values('day')
    cash_sales_values = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('cash_receipt__date', 'day', output_field=DateField(), )). \
        values('day')
    sales = sales_values.annotate(total=Sum('total')).order_by('day')
    cash_sales = cash_sales_values.annotate(total=Sum('total')).order_by('day')
    all_sales = []
    final_sales = []
    for sale in sales:
        all_sales.append({
            'day': sale['day'],
            'customer': sale['total'],
            'cash': 0
        })
    for sale in cash_sales:
        all_sales.append({
            'day': sale['day'],
            'cash': sale['total'],
            'customer': 0
        })
    all_sales.sort(key=lambda x: x['day'])
    for k, v in groupby(all_sales, key=lambda x: x['day']):
        v = list(v)
        final_sales.append({
            'day': k,
            'cash': sum(d['cash'] for d in v),
            'sales': sum(d['customer'] for d in v),
        })
    total_sales = sales.aggregate(Sum('total'))
    total_cash_sales = cash_sales.aggregate((Sum('total')))
    page = request.GET.get('payed_page', 1)

    paginator = Paginator(final_sales, 10)
    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)
    context_data = {'sales': sales, 'date_0': date_0_datetime, 'date_1': date_1_datetime,
                    'total_sales': total_sales, 'total_cash_sales': total_cash_sales,
                    'date_0_str': date_0_str, 'date_1_str': date_1_str,
                    'period': period}
    return render(request, 'reports/daily_sales/report.html', context_data)


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


@api_view(['GET'])
def get_json_response(request, date_0, date_1):
    period = get_date_period_in_range(date_0, date_1)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('receipt__date', period, output_field=DateField(), )). \
        values('day').annotate(total=Sum('total')).order_by('day')
    cash_sales = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('cash_receipt__date', period, output_field=DateField(), )). \
        values('day').annotate(total=Sum('total')).order_by('day')
    all_sales = []
    final_sales = []
    for sale in sales:
        all_sales.append({
            'day': sale['day'],
            'customer': sale['total'],
            'cash': 0
        })
    for sale in cash_sales:
        all_sales.append({
            'day': sale['day'],
            'cash': sale['total'],
            'customer': 0
        })
    all_sales.sort(key=lambda x: x['day'])
    for k, v in groupby(all_sales, key=lambda x: x['day']):
        v = list(v)
        final_sales.append({
            'day': k,
            'cash': sum(d['cash'] for d in v),
            'sales': sum(d['customer'] for d in v),
        })
    sales_summary_over_time = [{
        'period': x['day'],
        'customer': x['sales'] or 0,
        'cash': x['cash'] or 0,
    } for x in final_sales]
    serializer = CustomDailySalesChartSerializer(sales_summary_over_time, many=True)
    print(serializer.data)
    return Response(serializer.data)
