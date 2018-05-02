import datetime

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, DecimalField, F
from django.shortcuts import render, redirect

from core.models import Product
from sales import models
from django.contrib.auth.decorators import login_required
from reports import forms


# Create your views here.
@login_required()
def index(request):
    return render(request, 'reports/index.html')


@login_required()
def sale_summary_report(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('cash-sales-summary', date_0=date_0, date_1=date_1)
    else:
        form = forms.SaleSummaryDate(initial={'date_0': datetime.date.today(), 'date_1': datetime.date.today()})
    return render(request, 'reports/sales-summary.html', {'form': form})


@login_required()
def cash_sale_summary_report(request, date_0, date_1):
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0 = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1 = datetime.datetime.combine(date_1, datetime.time(23, 59))
    customer_report = models.CustomerAccount.objects.filter(via='C', date__range=(date_0, date_1))
    if customer_report.exists():
        customer_total_amount_cash = customer_report.aggregate(total_amount=Sum('amount'))
    else:
        customer_total_amount_cash = {'total_amount': 0}
    customer_receipts = customer_report.values(
        'receipt__number', 'customer__number').annotate(total_amount=Sum('amount')).order_by('-total_amount')
    customer_page = request.GET.get('customer_page', 1)
    paginator = Paginator(customer_receipts, 5)
    try:
        customer_receipts = paginator.page(customer_page)
    except PageNotAnInteger:
        customer_receipts = paginator.page(1)
    except EmptyPage:
        customer_receipts = paginator.page(paginator.num_pages)
    cash_report = models.CashReceiptParticular.objects.filter(cash_receipt__date__range=(date_0, date_1))
    if cash_report.exists():
        cash_total_amount_cash = cash_report.aggregate(total_amount=Sum(F('qty') * F('price')))
    else:
        cash_total_amount_cash = {'total_amount': 0}
    cash_receipts = cash_report.values('cash_receipt__number').annotate(total_amount=Sum(F('qty') * F('price')))
    cash_page = request.GET.get('cash_page', 1)
    paginator = Paginator(cash_receipts, 5)
    try:
        cash_receipts = paginator.page(cash_page)
    except PageNotAnInteger:
        cash_receipts = paginator.page(1)
    except EmptyPage:
        cash_receipts = paginator.page(paginator.num_pages)
    total_cash_summary = customer_total_amount_cash['total_amount'] + cash_total_amount_cash['total_amount']
    args = {
        'customer_total_amount_cash': customer_total_amount_cash,
        'customer_receipts': customer_receipts,
        'cash_receipts': cash_receipts,
        'cash_total_amount_cash': cash_total_amount_cash,
        'total_cash_summary': total_cash_summary,
        'date_0': date_0,
        'date_1': date_1
    }
    return render(request, 'reports/cash-sale_summary.html', args)


@login_required()
def mpesa_sale_summary_report(request, date_0, date_1):
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0 = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1 = datetime.datetime.combine(date_1, datetime.time(23, 59))
    customer_report = models.CustomerAccount.objects.filter(via='M', date__range=(date_0, date_1))
    if customer_report.exists():
        customer_total_amount_cash = customer_report.aggregate(total_amount=Sum('amount'))
    else:
        customer_total_amount_cash = {'total_amount': 0}
    customer_receipts = customer_report.values(
        'receipt__number', 'phone_number', 'customer__number').annotate(total_amount=Sum('amount')).order_by(
        '-total_amount')
    customer_page = request.GET.get('customer_page', 1)
    paginator = Paginator(customer_receipts, 5)
    try:
        customer_receipts = paginator.page(customer_page)
    except PageNotAnInteger:
        customer_receipts = paginator.page(1)
    except EmptyPage:
        customer_receipts = paginator.page(paginator.num_pages)
    args = {
        'customer_total_amount_cash': customer_total_amount_cash,
        'customer_receipts': customer_receipts,
        'date_0': date_0,
        'date_1': date_1
    }
    return render(request, 'reports/mpesa_sale_summary.html', args)
