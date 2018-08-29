import datetime
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from pytz import timezone as pytz_zone
from weasyprint import HTML

from core.models import Product, AggregationCenterProduct
from reports import forms
from sales import models

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


# todo add the right permissions
@login_required()
def outward_product_summary_period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('outward_product_report',
                            date_0=date_0, date_1=date_1)
    else:
        form = forms.SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                              'date_1': datetime.date.today()})
    return render(request, 'reports/outward-products/outward-product-period.html',
                  {'form': form})


# todo add the right permissions
# todo a proposal, let a faster language like go, do the reports and use django to render the data.That should be later
# todo for now, just try to aggregate on writes. Like calculating totals on save of an item and read the main aggregates
@login_required()
def outward_product_summary_report(request, date_0: str, date_1: str):
    """
    :param request:
    :param date_0:
    :param date_1:
    :return:
    """
    str_date_0 = date_0
    str_date_1 = date_1
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = datetime.datetime.combine(date_1, datetime.time(23, 59))
    outward = []
    for product in Product.objects.all():
        if models.OrderProduct.objects. \
                filter(product=product,
                       order__date_delivery__range=(
                               date_0, date_1)).exists() is False and models.PackageProduct.objects. \
                filter(order_product__product=product,
                       order_product__order__date_delivery__range=(
                               date_0, date_1)).exists() is False and models.OrderlessPackage.objects. \
                filter(product=product,
                       date__range=(date_0, date_1)).exists() is False and models.ReceiptParticular.objects. \
                filter(product=product, receipt__date__range=(
                date_0_datetime, date_1_datetime)).exists() is False and models.CashReceiptParticular.objects. \
                filter(product=product, cash_receipt__date__range=(
                date_0_datetime, date_1_datetime)).exists() is False and AggregationCenterProduct.objects.filter(
            product=product,
            date__range=(
                    date_0, date_1)).exists() is False and models.MarketReturn.objects. \
                filter(product=product, date__range=(date_0, date_1)).exists() is False:
            continue
        total_ordered = models.OrderProduct.objects. \
            filter(product=product, order__date_delivery__range=(date_0, date_1)). \
            aggregate(total=Sum('qty'))
        total_packaged = models.PackageProduct.objects. \
            filter(order_product__product=product,
                   order_product__order__date_delivery__range=(date_0, date_1)). \
            aggregate(total=Sum('qty_weigh'))
        total_orderless = models.OrderlessPackage.objects. \
            filter(product=product,
                   date__range=(date_0, date_1)). \
            aggregate(total=Sum('qty'))
        total_customer = models.ReceiptParticular.objects. \
            filter(product=product, receipt__date__range=(date_0_datetime, date_1_datetime)). \
            aggregate(total=Sum('qty'))
        total_cash = models.CashReceiptParticular.objects. \
            filter(product=product, cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
            aggregate(total=Sum('qty'))
        available = AggregationCenterProduct.objects.filter(product=product,
                                                            date__range=(date_0, date_1)). \
            values('aggregation_center__name').annotate(total=Sum('qty'))
        total_available = AggregationCenterProduct.objects.filter(product=product,
                                                                  date__range=(date_0, date_1)). \
            aggregate(total=Sum('qty'))
        if not total_available['total']:
            total_available['total'] = 0
        total_return = models.MarketReturn.objects. \
            filter(product=product, date__range=(date_0, date_1)). \
            aggregate(total=Sum('qty'))
        if not total_return['total']:
            total_return['total'] = 0
        if not total_customer['total']:
            total_customer['total'] = 0
        if not total_cash['total']:
            total_cash['total'] = 0
        if not total_packaged['total']:
            total_packaged['total'] = 0
        if not total_orderless['total']:
            total_orderless['total'] = 0
        total_dispatch = total_packaged['total'] + total_orderless['total']
        total_sale = total_customer['total'] + total_cash['total']
        variance = total_dispatch - total_sale - total_return['total']
        outward.append({'product': product.name, 'ordered': total_ordered['total'],
                        'packaged': total_packaged['total'],
                        'orderless': total_orderless['total'],
                        'total_dispatch': total_dispatch,
                        'customer': total_customer['total'],
                        'cash': total_cash['total'],
                        'total_sale': total_sale,
                        'available': available,
                        'total_available': total_available['total'],
                        'diff': variance,
                        'total_return': total_return['total'],
                        'product_id': product.pk})
    return render(request, 'reports/outward-products/report.html',
                  {'outwards': outward,
                   'date_0': date_0_datetime,
                   'date_1': date_1_datetime,
                   'str_date_0': str_date_0,
                   'str_date_1': str_date_1})


@login_required()
def outward_product_summary_alt_report(request, date_0: str, date_1: str):
    """
        :param request:
        :param date_0:
        :param date_1:
        :return:
        """
    str_date_0 = date_0
    str_date_1 = date_1
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    available = AggregationCenterProduct.objects.filter(date__range=(date_0, date_1)). \
        values('product__name').annotate(total=Sum('qty'))
    ordered = models.OrderProduct.objects. \
        filter(order__date_delivery__range=(date_0, date_1)). \
        values('product__name', 'product__pk').annotate(total=Sum('qty'))
    packaged = models.PackageProduct.objects. \
        filter(order_product__order__date_delivery__range=(date_0, date_1)). \
        values('order_product__product__name').annotate(total=Sum('qty_weigh'))
    orderless = models.OrderlessPackage.objects. \
        filter(date__range=(date_0, date_1)).values('product__name').annotate(total=Sum('qty'))
    customer = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime)).values('product__name'). \
        annotate(total=Sum('qty'))
    cash = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
        values('product__name').annotate(total=Sum('qty'))
    returns = models.MarketReturn.objects. \
        filter(date__range=(date_0, date_1)). \
        values('product__name').annotate(total=Sum('qty'))
    all_products = []
    for item in available:
        obj = {
            'product': item['product__name'],
            'available': item['total'],
            'ordered': 0,
            'packaged': 0,
            'orderless': 0,
            'customer': 0,
            'cash': 0,
            'total_sale': 0,
            'total_return': 0
        }
        all_products.append(obj)
    for item in ordered:
        obj = {
            'product': item['product__name'],
            'available': 0,
            'ordered': item['total'],
            'packaged': 0,
            'orderless': 0,
            'customer': 0,
            'cash': 0,
            'total_return': 0
        }
        all_products.append(obj)
    for item in packaged:
        obj = {
            'product': item['order_product__product__name'],
            'available': 0,
            'ordered': 0,
            'packaged': item['total'],
            'orderless': 0,
            'customer': 0,
            'cash': 0,
            'total_return': 0
        }
        all_products.append(obj)
    for item in orderless:
        obj = {
            'product': item['product__name'],
            'available': 0,
            'ordered': 0,
            'packaged': 0,
            'orderless': item['total'],
            'customer': 0,
            'cash': 0,
            'total_return': 0
        }
        all_products.append(obj)
    for item in customer:
        obj = {
            'product': item['product__name'],
            'available': 0,
            'ordered': 0,
            'packaged': 0,
            'orderless': 0,
            'customer': item['total'],
            'cash': 0,
            'total_return': 0
        }
        all_products.append(obj)
    for item in cash:
        obj = {
            'product': item['product__name'],
            'available': 0,
            'ordered': 0,
            'packaged': 0,
            'orderless': 0,
            'customer': 0,
            'cash': item['total'],
            'total_return': 0
        }
        all_products.append(obj)
    for item in returns:
        obj = {
            'product': item['product__name'],
            'available': 0,
            'ordered': 0,
            'packaged': 0,
            'orderless': 0,
            'customer': 0,
            'cash': 0,
            'total_return': item['total']
        }
        all_products.append(obj)
    outward = []
    all_products.sort(key=lambda x: x['product'])
    for k, v in groupby(all_products, key=lambda x: x['product']):
        v = list(v)
        obj = {
            'product': k,
            'available': sum(d['available'] for d in v),
            'ordered': sum(d['ordered'] for d in v),
            'packaged': sum(d['packaged'] for d in v),
            'orderless': sum(d['orderless'] for d in v),
            'customer': sum(d['customer'] for d in v),
            'cash': sum(d['cash'] for d in v),
            'total_return': sum(d['total_return'] for d in v),
            'total_available': sum(d['available'] for d in v),
        }
        if not obj['packaged'] and not obj['orderless']:
            obj['total_dispatch'] = 0
        elif not obj['packaged']:
            obj['total_dispatch'] = obj['orderless']
        elif not obj['orderless']:
            obj['total_dispatch'] = obj['packaged']
        else:
            obj['total_dispatch'] = obj['packaged'] + obj['orderless']
        if not obj['customer'] and not obj['cash']:
            obj['total_sale'] = 0
        elif not obj['customer']:
            obj['total_sale'] = obj['cash']
        elif not obj['cash']:
            obj['total_sale'] = obj['customer']
        else:
            obj['total_sale'] = obj['customer'] + obj['cash']
        obj['variance'] = obj['total_dispatch'] - obj['total_sale'] - obj['total_return' or 0]
        outward.append(obj)
    context = {'outwards': outward,
               'date_0': date_0_datetime,
               'date_1': date_1_datetime,
               'str_date_0': str_date_0,
               'str_date_1': str_date_1}
    download = request.GET.get('download', None)
    if download:
        invoice_string = render_to_string('reports/outward-products/outward_products_report_pdf.html', context)
        html = HTML(string=invoice_string)
        html.write_pdf(target='/tmp/outward_product_summary_from_{}_to_{}.pdf'.format(str_date_0, str_date_1))
        fs = FileSystemStorage('/tmp')
        with fs.open('outward_product_summary_from_{}_to_{}.pdf'.format(str_date_0, str_date_1)) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = "inline; filename='outward_product_summary_from_{}_to_{}.pdf'".format(
                str_date_0, str_date_1)
            return response
    return render(request, 'reports/outward-products/report.html', context)
