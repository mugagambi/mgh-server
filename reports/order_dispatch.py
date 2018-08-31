import datetime
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from pytz import timezone as pytz_zone

from reports import forms
from sales import models
from utils import handle_pdf_export

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('order_dispatch_report',
                            date_0=str(date_0), date_1=str(date_1))
    else:
        form = forms.SaleSummaryDate(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today(), })
    return render(request, 'reports/order-dispatch/period.html',
                  {'form': form})


@login_required()
def report(request, date_0, date_1):
    str_date_0 = date_0
    str_date_1 = date_1
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    orders = models.OrderProduct.objects.select_related('product').filter(
        order__created_at__range=(date_0_datetime, date_1_datetime)).values('product__name').annotate(Sum('qty'))
    customer_dispatch = models.PackageProduct.objects.select_related('order_product__product').filter(
        package__created_at__range=(date_0_datetime, date_1_datetime)).values('order_product__product__name').annotate(
        Sum('qty_weigh'))
    orderless_dispatch = models.OrderlessPackage.objects.select_related('product').filter(
        date__range=(date_0_datetime, date_1_datetime)).values('product__name').annotate(Sum('qty'))
    all_data = []
    for order in orders:
        all_data.append({
            'product': order['product__name'],
            'order_qty': order['qty__sum'],
            'customer_qty': 0,
            'orderless_qty': 0
        })
    for order in customer_dispatch:
        all_data.append({
            'product': order['order_product__product__name'],
            'order_qty': 0,
            'customer_qty': order['qty_weigh__sum'],
            'orderless_qty': 0
        })
    for order in orderless_dispatch:
        all_data.append({
            'product': order['product__name'],
            'order_qty': 0,
            'customer_qty': 0,
            'orderless_qty': order['qty__sum']
        })
    final_data = []
    all_data.sort(key=lambda x: x['product'])
    for k, v in groupby(all_data, key=lambda x: x['product']):
        v = list(v)
        order_qty = sum(d['order_qty'] for d in v)
        customer_qty = sum(d['customer_qty'] for d in v)
        orderless_qty = sum(d['orderless_qty'] for d in v)
        total_dispatch = customer_qty + orderless_qty
        final_data.append({
            'product': k,
            'order_qty': order_qty,
            'customer_qty': customer_qty,
            'orderless_qty': orderless_qty,
            'total_dispatch': total_dispatch,
            'variance': total_dispatch - order_qty
        })
    total_orders = orders.aggregate(Sum('qty__sum'))
    total_customer_dispatch = customer_dispatch.aggregate(Sum('qty_weigh__sum'))
    total_orderless = orderless_dispatch.aggregate(Sum('qty__sum'))
    context = {'data': final_data, 'total_order': total_orders, 'customer_dispatch': total_customer_dispatch,
               'orderless_dispatch': total_orderless, 'date_0': date_0_datetime, 'date_1': date_1_datetime}
    download = request.GET.get('download', None)
    if download:
        filename = 'orders_vs_dispatch_from_{}_to_{}'.format(str_date_0, str_date_1)
        return handle_pdf_export(folder='/tmp', filename=filename, context=context,
                                 template='reports/order-dispatch/report_pdf.html')
    return render(request, 'reports/order-dispatch/report.html', context)
