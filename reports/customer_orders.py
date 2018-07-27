# todo add the right permissions
import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from pytz import timezone as pytz_zone

from reports import forms
from sales import models

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.CustomerPerformance(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            customer = form.cleaned_data['customer']
            return redirect('customer_order_report',
                            date_0=date_0, date_1=date_1, customer=customer.pk)
    else:
        form = forms.CustomerPerformance(initial={'date_0': timezone.datetime.today(),
                                                  'date_1': timezone.datetime.today()})
    return render(request, 'reports/customer-order/period.html',
                  {'form': form})


def report(request, date_0, date_1, customer):
    customer = get_object_or_404(models.Customer, pk=customer)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    orders = models.OrderProduct.objects.filter(order__created_at__range=(date_0_datetime, date_1_datetime),
                                                order__customer=customer). \
        values('product__name').annotate(Sum('qty')).order_by('product__name')
    context = {'date_0': date_0_datetime, 'date_1': date_1_datetime, 'orders': orders, 'customer': customer}
    return render(request, 'reports/customer-order/report.html', context)
