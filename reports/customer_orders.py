# todo add the right permissions
import datetime
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from pytz import timezone as pytz_zone

from reports import forms
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
            customer = form.cleaned_data['customer']
            return redirect('customer_order_report',
                            date_0=date_0, date_1=date_1, customer=customer.pk)
    else:
        form = forms.CustomerPerformance(initial={'date_0': timezone.datetime.today(),
                                                  'date_1': timezone.datetime.today()})
    return render(request, 'reports/customer-order/period.html',
                  {'form': form})


def report(request, date_0, date_1, customer):
    str_date_0 = date_0
    str_date_1 = date_1
    customer = get_object_or_404(models.Customer, pk=customer)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    orders = models.OrderProduct.objects.filter(order__created_at__range=(date_0_datetime, date_1_datetime),
                                                order__customer=customer). \
        values('product__name').annotate(Sum('qty')).order_by('product__name')
    packages = models.PackageProduct.objects.filter(
        order_product__order__date_delivery__range=(date_0_datetime, date_1_datetime),
        order_product__order__customer=customer).values('order_product__product__name').annotate(
        Sum('qty_weigh')).order_by('order_product__product__name')
    temp_data = []
    for order in orders:
        temp_data.append({
            'product': order['product__name'],
            'order': order['qty__sum'],
            'packaged': 0,
        })
    for package in packages:
        temp_data.append({
            'product': package['order_product__product__name'],
            'order': 0,
            'packaged': package['qty_weigh__sum'],
        })
    temp_data.sort(key=lambda x: x['product'])
    final_data = []
    for k, v in groupby(temp_data, key=lambda x: x['product']):
        v = list(v)
        orders = sum(d['order'] for d in v)
        packages = sum(d['packaged'] for d in v)
        variance = packages - orders
        final_data.append({
            'product': k,
            'order': orders,
            'packages': packages,
            'variance': variance
        })
    total_orders = sum(d['order'] for d in final_data)
    total_packages = sum(d['packages'] for d in final_data)
    total_variance = total_packages - total_orders
    context = {'date_0': date_0_datetime, 'date_1': date_1_datetime, 'data': final_data, 'customer': customer,
               'total_orders': total_orders, 'total_packages': total_packages, 'total_variance': total_variance}
    download = request.GET.get('download', None)
    if download:
        filename = 'customer_orders_vs_dispatch_from_{}_to_{}'.format(str_date_0, str_date_1)
        return handle_pdf_export(folder='/tmp', filename=filename, context=context,
                                 template='reports/customer-order/report_pdf.html')
    return render(request, 'reports/customer-order/report.html', context)
