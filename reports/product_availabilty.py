from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from pytz import timezone as pytz_zone

from core import models
from reports import forms

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('product_availability_report',
                            date_0=str(date_0), date_1=str(date_1))
    else:
        form = forms.SaleSummaryDate(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today(), })
    return render(request, 'reports/product-availability/period.html',
                  {'form': form})


def report(request, date_0, date_1):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    products = models.AggregationCenterProduct.objects. \
        filter(date__range=(date_0, date_1)). \
        values('product__name').annotate(total_qty=Sum('qty')).order_by('product__name')
    context = {'date_0': date_0, 'date_1': date_1, 'products': products}
    return render(request, 'reports/product-availability/report.html', context)
