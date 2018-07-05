# todo add the right permissions
import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max, DateField, Sum, Avg
from django.db.models.functions import Trunc
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from reports import forms
from sales import models


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
        form = forms.CustomerPerformance(initial={'date_0': datetime.date.today(),
                                                  'date_1': datetime.date.today(), })
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
    period = get_date_period_in_range(date_0, date_1)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59))
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
    performance_over_time = [{
        'period': x['period'],
        'total': x['total'] or 0,
        'pct': ((x['total'] or 0) - low) / (high - low) * 100 if high > low else 0, } for x in sales]
    context_data = {'performance_over_time': performance_over_time, 'date_0': date_0_datetime,
                    'date_1': date_1_datetime, 'customer': customer, 'period': period,
                    'products': products, 'high': high, 'low': low, 'average': average,
                    'total_purchase': total_purchase}
    return render(request, 'reports/customer_performance/report.html', context_data)
