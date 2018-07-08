import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Max, Min, Avg, IntegerField, Sum, Count
from django.db.models.functions import Cast
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from pytz import timezone as pytz_zone

from core.models import Product
from reports import forms
from sales.models import ReceiptParticular, CashReceiptParticular

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


# todo add the right permissions
@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('price_per_product_report',
                            date_0=date_0, date_1=date_1)
    else:
        form = forms.SaleSummaryDate(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today()})
    return render(request, 'reports/price_per_product/period.html',
                  {'form': form})


# todo add the right permissions
@login_required()
def report(request, date_0, date_1):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    customer_sales = ReceiptParticular.objects.select_related('product').filter(
        receipt__date__range=(date_0_datetime, date_1_datetime)).values(
        'product__name', 'product__pk').annotate(Max('price'), Avg('price'),
                                                 Min('price')).order_by('product__name')
    cash_sales = CashReceiptParticular.objects.select_related('product').filter(
        cash_receipt__date__range=(date_0_datetime, date_1_datetime)).values('product__name', 'product__pk').annotate(
        Max('price'),
        Avg('price'),
        Min(
            'price')).order_by(
        'product__name')
    context = {'customer_sales': customer_sales, 'cash_sales': cash_sales, 'date_0': date_0_datetime,
               'date_1': date_1_datetime, 'date_0_str': str(date_0), 'date_1_str': str(date_1)}
    return render(request, 'reports/price_per_product/report.html', context)


# todo add the right permissions
@login_required()
def product_prices(request, product_id, type, date_0, date_1):
    product = get_object_or_404(Product, pk=product_id)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    if type == 'customer':
        sales = ReceiptParticular.objects.annotate(as_integer=Cast('price', IntegerField())).filter(
            receipt__date__range=(date_0_datetime, date_1_datetime), product=product).values(
            'as_integer').annotate(
            Sum('total'), Sum('qty'), Count('total')).order_by('-total__sum')
        context = {'product': product, 'sales': sales, 'type': 'Customer Sales', 'date_0': date_0_datetime,
                   'date_1': date_1_datetime}
    else:
        sales = CashReceiptParticular.objects.annotate(as_integer=Cast('price', IntegerField())).filter(
            cash_receipt__date__range=(date_0_datetime, date_1_datetime), product=product).values(
            'as_integer').annotate(
            Sum('total'), Count('total')).order_by('-total__sum')
        context = {'product': product, 'sales': sales, 'type': 'Open Air Market Sales', 'date_0': date_0_datetime,
                   'date_1': date_1_datetime}
    context['date_0_str'] = str(date_0)
    context['date_1_str'] = str(date_1)
    return render(request, 'reports/price_per_product/product_prices.html', context)


def customer_sales_per_price(request, product_id, price, type, date_0, date_1):
    product = get_object_or_404(Product, pk=product_id)
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    if type == 'Customer Sales':
        sales = ReceiptParticular.objects.select_related('product', 'receipt__customer', 'receipt',
                                                         'receipt__served_by').annotate(
            as_integer=Cast('price', IntegerField())).filter(
            receipt__date__range=(date_0_datetime, date_1_datetime), product=product, as_integer=price).order_by(
            'receipt__date')
        context = {'product': product, 'type': 'Customer Sales', 'date_0': date_0_datetime,
                   'date_1': date_1_datetime, 'price': price}
    else:
        sales = CashReceiptParticular.objects.select_related('product', 'cash_receipt',
                                                             'cash_receipt__served_by').annotate(
            as_integer=Cast('price', IntegerField())).filter(
            cash_receipt__date__range=(date_0_datetime, date_1_datetime), product=product, as_integer=price).order_by(
            'cash_receipt__date')
        context = {'product': product, 'type': 'Open Air Market Sales', 'date_0': date_0_datetime,
                   'date_1': date_1_datetime, 'price': price}
    totals = sales.aggregate(Sum('qty'), Sum('total'))
    context['totals'] = totals
    page = request.GET.get('payed_page', 1)

    paginator = Paginator(sales, 20)
    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)
    context['sales'] = sales
    return render(request, 'reports/price_per_product/sales.html', context)
