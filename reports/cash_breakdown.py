import datetime
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import DateField, Sum
from django.db.models.functions import Trunc
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from pytz import timezone as pytz_zone
from weasyprint import HTML

from cash_breakdown.models import CashDeposit, CashExpense
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
            return redirect('cash_breakdown_report',
                            date_0=str(date_0), date_1=str(date_1))
    else:
        form = forms.SaleSummaryDate(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today(), })
    return render(request, 'reports/daily-cash-breakdown/period.html',
                  {'form': form})


@login_required()
def report(request, date_0, date_1):
    date_0_str = date_0
    date_1_str = date_1
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    customer_sales = models.CustomerAccount.objects.filter(via='C', date__range=(date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('date', 'day', output_field=DateField(), )). \
        values('day').annotate(Sum('amount'))
    print(models.CustomerAccount.objects.filter(via='C', date__range=(date_0_datetime, date_1_datetime)))
    cash_sales = models.CashReceiptPayment.objects.filter(type=2,
                                                          cash_receipt__date__range=
                                                          (date_0_datetime, date_1_datetime)). \
        annotate(day=Trunc('cash_receipt__date', 'day', output_field=DateField(), )). \
        values('day').annotate(Sum('amount'))
    deposits = CashDeposit.objects.filter(date__range=(date_0, date_1)).values('date').annotate(Sum('amount'))
    expenses = CashExpense.objects.filter(date__range=(date_0, date_1)).values('date').annotate(Sum('amount'))
    temp_data = []
    for sale in customer_sales:
        d = {
            'day': sale['day'],
            'customer': sale['amount__sum'],
            'cash': 0,
            'deposit': 0,
            'expense': 0,
            'customer_deposits': 0
        }
        temp_data.append(d)
    for sale in cash_sales:
        d = {
            'day': sale['day'],
            'customer': 0,
            'cash': sale['amount__sum'],
            'deposit': 0,
            'expense': 0,
            'customer_deposits': 0
        }
        temp_data.append(d)
    for deposit in deposits:
        d = {
            'day': deposit['date'],
            'customer': 0,
            'cash': 0,
            'deposit': deposit['amount__sum'],
            'expense': 0,
            'customer_deposits': 0
        }
        temp_data.append(d)
    for expense in expenses:
        d = {
            'day': expense['date'],
            'customer': 0,
            'cash': 0,
            'deposit': 0,
            'expense': expense['amount__sum'],
            'customer_deposits': 0
        }
        temp_data.append(d)
    temp_data.sort(key=lambda x: x['day'])
    data = []
    for k, v in groupby(temp_data, key=lambda x: x['day']):
        v = list(v)
        data.append({
            'day': k,
            'cash_collected': sum(d['customer'] for d in v) + sum(d['cash'] for d in v) + sum(
                d['customer_deposits'] for d in v),
            'deposit': sum(d['deposit'] for d in v),
            'expense': sum(d['expense'] for d in v),
            'variance': (sum(d['customer'] for d in v) + sum(d['cash'] for d in v) + sum(
                d['customer_deposits'] for d in v)) - sum(d['deposit'] for d in v) - sum(d['expense'] for d in v)
        })
    total_collected = sum(d['cash_collected'] for d in data)
    deposits = sum(d['deposit'] for d in data)
    expenses = sum(d['expense'] for d in data)
    variance = total_collected - deposits - expenses
    context_data = {'date_0_str': date_0_str, 'date_1_str': date_1_str, 'date_0': date_0_datetime,
                    'date_1': date_1_datetime, 'data': data, 'total_collected': total_collected,
                    'deposits': deposits, 'expenses': expenses, 'variance': variance}
    download = request.GET.get('download', None)
    if download:
        invoice_string = render_to_string('reports/daily-cash-breakdown/daily_cash_breakdown_pdf.html', context_data)
        html = HTML(string=invoice_string)
        html.write_pdf(target='/tmp/daily_cash_breakdown_from_{}_to_{}.pdf'.format(date_0_str, date_1_str))
        fs = FileSystemStorage('/tmp')
        with fs.open('daily_cash_breakdown_from_{}_to_{}.pdf'.format(date_0_str, date_1_str)) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = "inline; filename='daily_cash_breakdown_from_{}_to_{}.pdf'".format(
                date_0_str, date_1_str)
            return response
    return render(request, 'reports/daily-cash-breakdown/report.html', context_data)
