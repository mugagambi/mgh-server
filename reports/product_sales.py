# todo add the right permissions
import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from pytz import timezone as pytz_zone

from reports import forms
from sales import models

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
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime)).values('product__name').annotate(
        Sum('qty'), Sum('total')).order_by('-total__sum')
    cash_sales = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime)).values('product__name').annotate(
        Sum('qty'), Sum('total')).order_by('-total__sum')
    total_sales_qty = sales.aggregate(Sum('qty__sum'))
    total_sales_amount = sales.aggregate(Sum('total__sum'))
    total_cash_sales_qty = cash_sales.aggregate(Sum('qty__sum'))
    total_cash_sales_amount = cash_sales.aggregate(Sum('total__sum'))
    context = {'date_0': date_0_datetime, 'date_1': date_1_datetime, 'sales': sales, 'cash_sales': cash_sales,
               'total_sales_qty': total_sales_qty, 'total_sales_amount': total_sales_amount,
               'total_cash_sales_qty': total_cash_sales_qty, 'total_cash_sales_amount': total_cash_sales_amount}
    return render(request, 'reports/product-sales/report.html', context)
