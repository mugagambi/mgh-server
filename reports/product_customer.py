import datetime
from itertools import groupby
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML

from core.models import Product
from reports import forms
from sales import models
from utils import export_pdf


@login_required()
def outward_product_customer_summary_period(request):
    if request.method == 'POST':
        form = forms.ProductCustomer(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            product = form.cleaned_data['product']
            return redirect('outward-product-per-customer',
                            date_0=date_0, date_1=date_1, product_id=product.id)
    else:
        form = forms.ProductCustomer(initial={'date_0': datetime.date.today(),
                                              'date_1': datetime.date.today()})
    return render(request, 'reports/outward-product-customer/date-period.html',
                  {'form': form})


@login_required()
def outward_product_summary_report_alt(request, date_0, date_1, product_id):
    str_date_0 = date_0
    str_date_1 = date_1
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = datetime.datetime.combine(date_1, datetime.time(23, 59))
    product = get_object_or_404(Product, pk=product_id)
    orders = models.OrderProduct.objects.select_related('product', 'order__customer'). \
        filter(product=product, order__date_delivery__range=(date_0_datetime, date_1_datetime)).values(
        'order__customer__shop_name').annotate(Sum('qty')).order_by('order__customer__shop_name')
    packaged = models.PackageProduct.objects.select_related('order_product__product', 'order_product__order',
                                                            'order_product__order__customer'). \
        filter(order_product__product=product,
               order_product__order__date_delivery__range=(date_0_datetime, date_1_datetime)).values(
        'order_product__order__customer__shop_name').annotate(Sum('qty_weigh')).order_by(
        'order_product__order__customer__shop_name')
    sold = models.ReceiptParticular.objects.select_related('product', 'receipt__customer', 'receipt').filter(
        product=product, receipt__date__range=(
            date_0_datetime, date_1_datetime)).values('receipt__customer__shop_name').annotate(Sum('qty')).order_by(
        'receipt__customer__shop_name')
    returns = models.Return.objects.select_related('product', 'customer'). \
        filter(product=product, date__range=(date_0_datetime, date_1_datetime)).values('customer__shop_name'). \
        annotate(Sum('qty')).order_by('customer__shop_name')

    temp_data = []
    for order in orders:
        temp_data.append({
            'customer': order['order__customer__shop_name'],
            'ordered': order['qty__sum'],
            'packaged': 0,
            'total_sold': 0,
            'total_return': 0
        })
    for package in packaged:
        temp_data.append({
            'customer': package['order_product__order__customer__shop_name'],
            'ordered': 0,
            'packaged': package['qty_weigh__sum'],
            'total_sold': 0,
            'total_return': 0
        })
    for sale in sold:
        temp_data.append({
            'customer': sale['receipt__customer__shop_name'],
            'ordered': 0,
            'packaged': 0,
            'total_sold': sale['qty__sum'],
            'total_return': 0
        })
    for returned in returns:
        temp_data.append({
            'customer': returned['customer__shop_name'],
            'ordered': 0,
            'packaged': 0,
            'total_sold': 0,
            'total_return': returned['qty__sum']
        })
    temp_data.sort(key=lambda x: x['customer'])
    outwards = []
    for k, v in groupby(temp_data, key=lambda x: x['customer']):
        v = list(v)
        packed = sum(d['packaged'] for d in v)
        sold = sum(d['total_sold'] for d in v)
        returned = sum(d['total_return'] for d in v)
        outwards.append({
            'customer': k,
            'ordered': sum(d['ordered'] for d in v),
            'packaged': packed,
            'total_sold': sold,
            'total_return': returned,
            'variance': packed - sold - returned
        })
    total_ordered = sum(d['ordered'] for d in outwards)
    total_packaged = sum(d['packaged'] for d in outwards)
    total_sold = sum(d['total_sold'] for d in outwards)
    total_return = sum(d['total_return'] for d in outwards)
    variance = total_packaged - total_sold - total_return
    context = {'outwards': outwards,
               'date_0': date_0_datetime,
               'date_1': date_1_datetime,
               'product': product,
               'total_ordered': total_ordered,
               'total_packaged': total_packaged,
               'total_sold': total_sold,
               'total_return': total_return,
               'variance': variance}
    download = request.GET.get('download', None)
    if download:
        folder = '/tmp'
        filename = 'product_summary_per_customer_from_{}_to_{}.pdf'.format(str_date_0, str_date_1)
        file = Path(filename)
        if not file.is_file():
            invoice_string = render_to_string('reports/outward-product-customer/report_pdf.html', context)
            html = HTML(string=invoice_string)
            html.write_pdf(target='/tmp/{filename}'.format(filename=filename))
        return export_pdf(folder, filename=filename)
    return render(request, 'reports/outward-product-customer/report.html', context)
