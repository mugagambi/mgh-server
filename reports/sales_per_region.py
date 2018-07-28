import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from pytz import timezone as pytz_zone

from reports import forms
from sales import models

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


# todo add the right permissions
@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('sales_per_region_report',
                            date_0=date_0, date_1=date_1)
    else:
        form = forms.SaleSummaryDate(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today()})
    return render(request, 'reports/sales-per-region/period.html',
                  {'form': form})


def report(request, date_0, date_1):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime)). \
        values('receipt__customer__region__name').annotate(Sum('total')).order_by('receipt__customer__region__name')
    cxt = {'sales': sales, 'date_0': date_0_datetime, 'date_1': date_1_datetime}
    return render(request, 'reports/sales-per-region/report.html', cxt)
