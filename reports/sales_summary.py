import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, F
from django.shortcuts import redirect, render

from reports import forms
from sales import models


# todo add the required permissions
@login_required()
def sales_summary_schedule(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('sales_summary_report',
                            date_0=date_0, date_1=date_1)
    else:
        form = forms.SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                              'date_1': datetime.date.today()})
    return render(request, 'reports/sales-summary/sales-summary.html',
                  {'form': form})


# todo add the required permissions
# todo use the pre-aggregated data
@login_required()
def sales_summary_report(request, date_0, date_1):
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0 = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1 = datetime.datetime.combine(date_1, datetime.time(23, 59))
    payed = models.ReceiptPayment.objects.filter(receipt__date__range=(date_0, date_1)).exclude(type=4)
    if payed.exists():
        payed_total = payed.aggregate(total_amount=Sum('amount'))
    else:
        payed_total = {'total_amount': 0}
    payed_receipts = payed.values('receipt__number').annotate(total_amount=Sum('amount')).order_by(
        '-total_amount')
    cash_sale = models.CashReceiptParticular.objects.filter(cash_receipt__date__range=(date_0, date_1)).aggregate(
        total_amount=Sum(F('qty') * F('price')))
    credit = models.ReceiptPayment.objects.filter(receipt__date__range=(date_0, date_1), type=4)
    if credit.exists():
        credit_total = credit.aggregate(total_amount=Sum('amount'))
    else:
        credit_total = {'total_amount': 0}
    credit_receipts = credit.values('receipt__number').annotate(total_amount=Sum('amount')).order_by(
        '-total_amount')
    payed_page = request.GET.get('payed_page', 1)
    paginator = Paginator(payed_receipts, 5)
    try:
        payed_receipts = paginator.page(payed_page)
    except PageNotAnInteger:
        payed_receipts = paginator.page(1)
    except EmptyPage:
        payed_receipts = paginator.page(paginator.num_pages)
    credit_page = request.GET.get('credit_page', 1)
    paginator = Paginator(credit_receipts, 5)
    try:
        credit_receipts = paginator.page(credit_page)
    except PageNotAnInteger:
        credit_receipts = paginator.page(1)
    except EmptyPage:
        credit_receipts = paginator.page(paginator.num_pages)
    args = {
        'payed_total': payed_total,
        'payed_receipts': payed_receipts,
        'cash_sale': cash_sale,
        'credit_total': credit_total,
        'credit_receipts': credit_receipts,
        'date_0': date_0,
        'date_1': date_1
    }
    return render(request, 'reports/sales-summary/sale_summary_report.html', args)
