import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import DateField, Sum, Min, Max
from django.db.models.functions import Trunc
from django.shortcuts import redirect, render
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from reports import forms
from sales import models
from .serializers import DailySalesChartSerializer


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
        form = forms.SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                              'date_1': datetime.date.today(), })
    return render(request, 'reports/daily_sales/period.html',
                  {'form': form})


def report(request, date_0, date_1):
    period = get_date_period_in_range(date_0, date_1)
    date_0_str = date_0
    date_1_str = date_1
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59))
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('receipt__date', 'day', output_field=DateField(), )). \
        values('day').annotate(total=Sum('total')).order_by('day')
    cash_sales = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('cash_receipt__date', 'day', output_field=DateField(), )). \
        values('day').annotate(total=Sum('total')).order_by('day')
    cash_sales_summary_range = cash_sales.aggregate(
        low=Min('total'),
        high=Max('total'),
    )
    high = cash_sales_summary_range.get('high', 0)
    low = cash_sales_summary_range.get('low', 0)
    cash_sales_summary_over_time = [{
        'period': x['day'],
        'total': x['total'] or 0,
        'pct':
            ((x['total'] or 0) - low) / (high - low) * 100
            if high > low else 0,
    } for x in cash_sales]
    total_sales = sales.aggregate(Sum('total'))
    total_cash_sales = cash_sales.aggregate((Sum('total')))
    page = request.GET.get('payed_page', 1)

    paginator = Paginator(sales, 10)
    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)
    page = request.GET.get('credit_page', 1)

    paginator = Paginator(cash_sales, 10)
    try:
        cash_sales = paginator.page(page)
    except PageNotAnInteger:
        cash_sales = paginator.page(1)
    except EmptyPage:
        cash_sales = paginator.page(paginator.num_pages)
    context_data = {'sales': sales, 'date_0': date_0_datetime, 'date_1': date_1_datetime, 'cash_sales': cash_sales,
                    'total_sales': total_sales, 'total_cash_sales': total_cash_sales,
                    'cash_sales_summary_over_time': cash_sales_summary_over_time,
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
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59))
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('receipt__date', period, output_field=DateField(), )). \
        values('day').annotate(total=Sum('total')).order_by('day')
    sales_summary_over_time = [{
        'period': x['day'],
        'total': x['total'] or 0,
    } for x in sales]
    serializer = DailySalesChartSerializer(sales_summary_over_time, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_cash_sale_json_response(request, date_0, date_1):
    period = get_date_period_in_range(date_0, date_1)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59))
    sales = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('cash_receipt__date', period, output_field=DateField(), )). \
        values('day').annotate(total=Sum('total')).order_by('day')
    sales_summary_over_time = [{
        'period': x['day'],
        'total': x['total'] or 0,
    } for x in sales]
    serializer = DailySalesChartSerializer(sales_summary_over_time, many=True)
    return Response(serializer.data)
