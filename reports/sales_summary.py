import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, F
from django.shortcuts import redirect, render

from reports import forms
from sales import models
# todo add the required permissions
from utils import handle_pdf_export


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
    str_date_0 = date_0
    str_date_1 = date_1
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0 = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1 = datetime.datetime.combine(date_1, datetime.time(23, 59))
    payed = models.ReceiptPayment.objects.select_related('receipt').filter(
        receipt__date__range=(date_0, date_1)).exclude(type=4).values('receipt_id')
    receipt_ids = [r['receipt_id'] for r in payed]
    receipts = models.Receipt.objects.filter(number__in=receipt_ids)
    if receipts.exists():
        payed_total = receipts.aggregate(total_amount=Sum('receiptparticular__total'))
    else:
        payed_total = {'total_amount': 0}
    print('disaster')
    payed_receipts = receipts.annotate(total_amount=Sum('receiptparticular__total')). \
        values('number', 'total_amount', 'date', 'customer__shop_name').order_by('date')
    cash_sale = models.CashReceiptParticular.objects.select_related('cash_receipt').filter(
        cash_receipt__date__range=(date_0, date_1)).aggregate(
        total_amount=Sum(F('qty') * F('price')))
    # todo stop aggregating total
    credit_payments = models.ReceiptPayment.objects.select_related('receipt').filter(
        receipt__date__range=(date_0, date_1), type=4)
    receipt_id = [payment.receipt_id for payment in credit_payments]
    credit = models.Receipt.objects.filter(number__in=receipt_id).annotate(
        Sum('receiptparticular__total')).values('number', 'receiptparticular__total__sum', 'date', 'customer__shop_name')
    if credit.exists():
        credit_total = credit.aggregate(total_amount=Sum('receiptparticular__total__sum'))
    else:
        credit_total = {'receiptparticular__total__sum': 0}
    credit_receipts = credit.order_by('date')
    pdf_context = {'payed_receipts': payed_receipts, 'date_0': date_0, 'date_1': date_1, 'payed_total': payed_total,
                   'cash_sale': cash_sale, 'credit_receipts': credit_receipts, 'credit_total': credit_total}
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
    download = request.GET.get('download', None)
    if download:
        filename = 'sales_summary_from_{}_to_{}'.format(str_date_0, str_date_1)
        return handle_pdf_export(folder='/tmp', filename=filename, context=pdf_context,
                                 template='reports/sales-summary/report_pdf.html')
    return render(request, 'reports/sales-summary/sale_summary_report.html', args)
