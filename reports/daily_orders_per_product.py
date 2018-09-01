import datetime
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import DateField, Sum
from django.db.models.functions import Trunc
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
        form = forms.ProductCustomer(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            product = form.cleaned_data['product']
            return redirect('daily_orders_product_report',
                            date_0=str(date_0), date_1=str(date_1), product=product.id)
    else:
        form = forms.ProductCustomer(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today(), })
    return render(request, 'reports/daily-orders-per-product/period.html',
                  {'form': form})


def report(request, date_0, date_1, product):
    str_date_0 = date_0
    str_date_1 = date_1
    product = get_object_or_404(models.Product, pk=product)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    orders = models.OrderProduct.objects. \
        filter(order__created_at__range=(date_0_datetime, date_1_datetime), product=product). \
        annotate(day=Trunc('order__created_at', 'day', output_field=DateField(), )). \
        values('day').annotate(Sum('qty')).order_by('day')
    packages = models.PackageProduct.objects.filter(
        order_product__order__date_delivery__range=(date_0_datetime, date_1_datetime),
        order_product__product=product).annotate(
        day=Trunc('order_product__order__date_delivery', 'day', output_field=DateField())).values('day').annotate(
        Sum('qty_weigh')).order_by('day')
    orderless_dispatch = models.OrderlessPackage.objects.select_related('product').filter(
        date__range=(date_0, date_1), product=product).annotate(
        day=Trunc('date', 'day', output_field=DateField())).values('day').annotate(
        Sum('qty')).order_by('day')
    temp_data = []
    for order in orders:
        temp_data.append({
            'day': order['day'],
            'order': order['qty__sum'],
            'packaged': 0,
            'orderless': 0
        })
    for package in packages:
        temp_data.append({
            'day': package['day'],
            'order': 0,
            'packaged': package['qty_weigh__sum'],
            'orderless': 0
        })
    for order in orderless_dispatch:
        temp_data.append({
            'day': order['day'],
            'order': 0,
            'packaged': 0,
            'orderless': order['qty__sum']
        })
    temp_data.sort(key=lambda x: x['day'])
    final_data = []
    for k, v in groupby(temp_data, key=lambda x: x['day']):
        v = list(v)
        orders = sum(d['order'] for d in v)
        packages = sum(d['packaged'] for d in v)
        orderless = sum(d['orderless'] for d in v)
        total_dispatch = packages + orderless
        variance = total_dispatch - orders
        final_data.append({
            'day': k,
            'order': orders,
            'packages': packages,
            'orderless': orderless,
            'total_dispatch': total_dispatch,
            'variance': variance
        })
    total_orders = sum(d['order'] for d in final_data)
    total_customer = sum(d['packages'] for d in final_data)
    total_orderless = sum(d['orderless'] for d in final_data)
    total_dispatch = sum(d['total_dispatch'] for d in final_data)
    total_variance = total_dispatch - total_orders
    page = request.GET.get('payed_page', 1)

    paginator = Paginator(final_data, 31)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context_data = {'orders': orders, 'date_0': date_0_datetime, 'date_1': date_1_datetime,
                    'total_orders': total_orders, 'total_dispatch': total_dispatch,
                    'product': product, 'variance': total_variance, 'total_customer': total_customer,
                    'total_orderless': total_orderless}
    download = request.GET.get('download', None)
    if download:
        filename = 'daily_orders_vs_dispatch_per_product_from_{}_to_{}'.format(str_date_0, str_date_1)
        return handle_pdf_export(folder='/tmp', filename=filename, context=context_data,
                                 template='reports/daily-orders-per-product/report_pdf.html')
    return render(request, 'reports/daily-orders-per-product/report.html', context_data)
