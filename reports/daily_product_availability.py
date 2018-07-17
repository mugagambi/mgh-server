from django.contrib.auth.decorators import login_required
from django.db.models import Sum, DateField
from django.db.models.functions import Trunc
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from pytz import timezone as pytz_zone

from core import models
from reports import forms
from reports.cash_deposit import get_date_period_in_range

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.ProductCustomer(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            product = form.cleaned_data['product']
            return redirect('daily_product_availability_report',
                            date_0=str(date_0), date_1=str(date_1), product=product.id)
    else:
        form = forms.ProductCustomer(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today(), })
    return render(request, 'reports/daily-product-availability/period.html',
                  {'form': form})


def report(request, date_0, date_1, product):
    product = get_object_or_404(models.Product, pk=product)
    period = get_date_period_in_range(date_0, date_1)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    items = models.AggregationCenterProduct.objects.filter(date__range=(date_0, date_1), product=product).values(
        'date').annotate(total_qty=Sum('qty')).order_by('date')
    items_graph = models.AggregationCenterProduct.objects.filter(date__range=(date_0, date_1),
                                                                 product=product).annotate(
        day=Trunc('date', period, output_field=DateField(), )).values('day').annotate(total_qty=Sum('qty')).order_by(
        'day')
    total = items.aggregate(Sum('total_qty'))['total_qty__sum']
    cxt = {'date_0': date_0, 'date_1': date_1, 'period': period, 'product': product, 'items': items,
           'items_graph': items_graph, 'total': total}
    return render(request, 'reports/daily-product-availability/report.html', cxt)
