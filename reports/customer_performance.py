# todo add the right permissions
import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max, DateField, Sum, Avg
from django.db.models.functions import Trunc
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from pytz import timezone as pytz_zone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from reports import forms
from reports.serializers import DailySalesChartSerializer
from sales import models
from utils import handle_pdf_export

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.CustomerPerformance(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            customer = form.cleaned_data['customer'].pk
            return redirect('customer_performance_report',
                            date_0=str(date_0), date_1=str(date_1), customer=customer)
    else:
        form = forms.CustomerPerformance(initial={'date_0': timezone.datetime.today(),
                                                  'date_1': timezone.datetime.today(), })
    return render(request, 'reports/customer_performance/period.html',
                  {'form': form})


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


# todo add the right permissions
@login_required()
def report(request, date_0, date_1, customer):
    date_0_str = date_0
    date_1_str = date_1
    period = get_date_period_in_range(date_0, date_1)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    customer = get_object_or_404(models.Customer, pk=customer)
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime),
               receipt__customer=customer). \
        annotate(period=Trunc('receipt__date', 'day', output_field=DateField(), )). \
        values('period').annotate(total=Sum('total')).order_by('period')
    summary_range = sales.aggregate(
        low=Min('total'),
        high=Max('total'),
    )
    average = sales.aggregate(average=Avg('total'))
    total_purchase = sales.aggregate(total_purchase=Sum('total'))
    products = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime),
               receipt__customer=customer).values('product__name'). \
        annotate(total_qty=Sum('qty'),
                 total_purchase=Sum('total')).order_by('-total_purchase')
    high = summary_range.get('high', 0)
    low = summary_range.get('low', 0)
    daily_sales_url = request.build_absolute_uri(
        reverse('customer_sales_report', kwargs={'date_0': date_0_str, 'date_1': date_1_str, 'customer': customer.pk}))
    context_data = {'date_0': date_0_datetime,
                    'date_1': date_1_datetime, 'customer': customer, 'period': period,
                    'products': products, 'high': high, 'low': low, 'average': average,
                    'total_purchase': total_purchase,
                    'date_0_str': date_0_str, 'date_1_str': date_1_str, 'daily_sales_url': daily_sales_url}
    download = request.GET.get('download', None)
    if download:
        filename = 'customer_performance_from_{}_to_{}'.format(date_0_str, date_1_str)
        return handle_pdf_export(folder='/tmp', filename=filename, context=context_data,
                                 template='reports/customer_performance/report_pdf.html')
    return render(request, 'reports/customer_performance/report.html', context_data)


@api_view(['GET'])
def get_json_response(request, date_0, date_1, customer):
    period = get_date_period_in_range(date_0, date_1)
    customer = get_object_or_404(models.Customer, pk=customer)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime),
               receipt__customer=customer). \
        annotate(day=Trunc('receipt__date', period, output_field=DateField(), )). \
        values('day').annotate(total=Sum('total')).order_by('day')
    sales_summary_over_time = [{
        'period': x['day'],
        'total': x['total'] or 0,
    } for x in sales]
    serializer = DailySalesChartSerializer(sales_summary_over_time, many=True)
    return Response(serializer.data)
