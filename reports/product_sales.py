# todo add the right permissions
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
            return redirect('product_sales_report',
                            date_0=date_0, date_1=date_1)
    else:
        form = forms.SaleSummaryDate(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today()})
    return render(request, 'reports/product-sales/period.html',
                  {'form': form})


def report(request, date_0, date_1):
    date_0_str = date_0
    date_1_str = date_1
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime)).values('product__name').annotate(
        Sum('qty'), Sum('total'))
    cash_sales = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime)).values('product__name').annotate(
        Sum('qty'), Sum('total'))
    all_sales = []
    final_sales = []
    for sale in sales:
        all_sales.append({
            'product__name': sale['product__name'],
            'customer_qty': sale['qty__sum'],
            'customer_total': sale['total__sum'],
            'cash_qty': 0,
            'cash_total': 0
        })
    for sale in cash_sales:
        all_sales.append({
            'product__name': sale['product__name'],
            'customer_qty': 0,
            'customer_total': 0,
            'cash_qty': sale['qty__sum'],
            'cash_total': sale['total__sum']
        })
    all_sales.sort(key=lambda x: x['product__name'])
    for k, v in groupby(all_sales, key=lambda x: x['product__name']):
        v = list(v)
        final_sales.append({
            'product__name': k,
            'customer_qty': sum(d['customer_qty'] for d in v),
            'customer_total': sum(d['customer_total'] for d in v),
            'cash_qty': sum(d['cash_qty'] for d in v),
            'cash_total': sum(d['cash_total'] for d in v),
        })
    total_sales_qty = sales.aggregate(Sum('qty__sum'))
    total_sales_amount = sales.aggregate(Sum('total__sum'))
    total_cash_sales_qty = cash_sales.aggregate(Sum('qty__sum'))
    total_cash_sales_amount = cash_sales.aggregate(Sum('total__sum'))
    context = {'date_0': date_0_datetime, 'date_1': date_1_datetime, 'sales': final_sales,
               'total_sales_qty': total_sales_qty, 'total_sales_amount': total_sales_amount,
               'total_cash_sales_qty': total_cash_sales_qty, 'total_cash_sales_amount': total_cash_sales_amount}
    download = request.GET.get('download', None)
    if download:
        filename = 'product_sales_from_{}_to_{}'.format(date_0_str, date_1_str)
        return handle_pdf_export(folder='/tmp', filename=filename, context=context,
                                 template='reports/product-sales/report_pdf.html')
    return render(request, 'reports/product-sales/report.html', context)
