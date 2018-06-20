import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min, Avg
from django.shortcuts import redirect, render
from django.utils import timezone

from reports import forms
from sales.models import ReceiptParticular, CashReceiptParticular


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
        form = forms.SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                              'date_1': datetime.date.today()})
    return render(request, 'reports/price_per_product/period.html',
                  {'form': form})


# todo add the right permissions
@login_required()
def report(request, date_0, date_1):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59))
    customer_sales = ReceiptParticular.objects.filter(receipt__date__range=(date_0_datetime, date_1_datetime)).values(
        'product__name').annotate(Max('price'), Avg('price'),
                                  Min('price')).order_by('product__name')
    cash_sales = CashReceiptParticular.objects.filter(
        cash_receipt__date__range=(date_0_datetime, date_1_datetime)).values('product__name').annotate(Max('price'),
                                                                                                       Avg('price'),
                                                                                                       Min(
                                                                                                           'price')).order_by(
        'product__name')
    context = {'customer_sales': customer_sales, 'cash_sales': cash_sales, 'date_0': date_0_datetime,
               'date_1': date_1_datetime}
    return render(request, 'reports/price_per_product/report.html', context)
