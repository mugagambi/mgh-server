import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import DateField, Sum
from django.db.models.functions import Trunc
from django.shortcuts import redirect, render
from django.utils import timezone

from reports import forms
from sales import models


@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('daily_sales_report',
                            date_0=str(date_0), date_1=str(date_1))
    else:
        form = forms.SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                              'date_1': datetime.date.today(), })
    return render(request, 'reports/daily_sales/period.html',
                  {'form': form})


def report(request, date_0, date_1):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59))
    sales = models.ReceiptParticular.objects. \
        filter(receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('receipt__date', 'day', output_field=DateField(), )). \
        values('day').annotate(total=Sum('total')).order_by('-day')
    cash_sales = models.CashReceiptParticular.objects. \
        filter(cash_receipt__date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('cash_receipt__date', 'day', output_field=DateField(), )). \
        values('day').annotate(total=Sum('total')).order_by('-day')
    total_sales = sales.aggregate(Sum('total'))
    total_cash_sales = cash_sales.aggregate((Sum('total')))
    page = request.GET.get('payed_page', 1)

    paginator = Paginator(sales, 10)
    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)
    page = request.GET.get('credit_page', 1)

    paginator = Paginator(cash_sales, 10)
    try:
        cash_sales = paginator.page(page)
    except PageNotAnInteger:
        cash_sales = paginator.page(1)
    except EmptyPage:
        cash_sales = paginator.page(paginator.num_pages)
    context_data = {'sales': sales, 'date_0': date_0_datetime, 'date_1': date_1_datetime, 'cash_sales': cash_sales,
                    'total_sales': total_sales, 'total_cash_sales': total_cash_sales}
    return render(request, 'reports/daily_sales/report.html', context_data)
