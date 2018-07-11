import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.views import View
from pytz import timezone as pytz_zone

from reports.forms import SaleSummaryDate
from sales import models
from sales import resources
from .render_pdf import render_to_pdf

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


# todo add the right permissions
@login_required()
def export_customers(request):
    customer_resource = resources.CustomerResource()
    dataset = customer_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customer_%s.csv"' % str(datetime.datetime.now())
    return response


# todo add the right permissions
@login_required()
def export_cash_sales_period(request):
    if request.method == 'POST':
        form = SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('pdf-cash',
                            date_0=date_0, date_1=date_1)
    else:
        form = SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                        'date_1': datetime.date.today()})
    return render(request, 'sales/resources/cash_sale_period.html',
                  {'form': form})


# todo add the right permissions
class GeneratePDF(LoginRequiredMixin, View):
    def get(self, request, date_0, date_1, *args, **kwargs):
        date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
        date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
        date_0_datetime = datetime.datetime.combine(date_0, datetime.time(0, 0))
        date_1_datetime = datetime.datetime.combine(date_1, datetime.time(23, 59))
        particulars = models.CashReceiptParticular.objects.filter(
            cash_receipt__date__range=(date_0_datetime, date_1_datetime)).select_related('product').annotate(
            total_sum=F('price') * F('qty')
        ).order_by('-cash_receipt__date')
        total_qty = particulars.aggregate(sum=Sum('qty'))
        total_amount = particulars.aggregate(total=Sum(F('qty') * F('price')))
        template = get_template('sales/resources/cash_sale.html')
        context = {
            "particulars": particulars,
            "total_qty": total_qty,
            'total_amount': total_amount,
            'date_0_datetime': date_0_datetime,
            'date_1_datetime': date_1_datetime,
        }
        html = template.render(context)
        pdf = render_to_pdf('sales/resources/cash_sale.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "cash_sale_from_%s_to_%s.pdf" % (date_0, date_1)
            content = "inline; filename='%s'" % filename
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % filename
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


# todo add the required permissions
@login_required()
def export_sales_period(request):
    if request.method == 'POST':
        form = SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('export-customer-sales',
                            date_0=date_0, date_1=date_1)
    else:
        form = SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                        'date_1': datetime.date.today()})
    return render(request, 'sales/resources/sales_period.html',
                  {'form': form})


# todo add the right permissions
@login_required()
def export_customer_sales(request, date_0, date_1):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    template = get_template('sales/resources/customer_sale_export.html')
    receipts = models.Receipt.objects.filter(date__range=(date_0_datetime, date_1_datetime)). \
        annotate(total_qty=Sum('receiptparticular__qty'), sub_total=Sum('receiptparticular__total'))
    receipt_amount = receipts.aggregate(total=Sum('receiptparticular__total'))
    total_balance = receipts.aggregate(total=Sum('receiptmisc__balance'))
    total_amount_payable = (receipt_amount['total'] or 0) - (total_balance['total'] or 0)
    total_payed = receipts.exclude(receiptpayment__type=4).aggregate(total=Sum('receiptpayment__amount'))
    credit = receipts.filter(receiptpayment__type=4)
    receipt_id = [payment.number for payment in credit]
    total_credit = models.Receipt.objects.filter(number__in=receipt_id).values('number').aggregate(
        total=Sum('receiptparticular__total'))
    total_payed_amount = (total_payed['total'] or 0) + (total_credit['total'] or 0)
    context = {
        'date_0_datetime': date_0_datetime,
        'date_1_datetime': date_1_datetime,
        'receipts': receipts,
        'receipt_amount': (receipt_amount['total'] or 0),
        'total_balance': (total_balance['total'] or 0),
        'total_amount_payable': total_amount_payable,
        'total_payed': (total_payed['total'] or 0),
        'total_credit': (total_credit['total'] or 0),
        'total_payed_amount': total_payed_amount
    }
    html = template.render(context)
    pdf = render_to_pdf('sales/resources/customer_sale_export.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "customer_sales_from_%s_to_%s.pdf" % (date_0, date_1)
        content = "inline; filename='%s'" % filename
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" % filename
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required()
def export_customer_statement_period(request, customer):
    customer = get_object_or_404(models.Customer, pk=customer)
    if request.method == 'POST':
        form = SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            url = reverse('customer_statement_export',
                          kwargs={'date_0': date_0, 'date_1': date_1,
                                  'customer': customer.pk})
            return redirect(url + '?download=true')
    else:
        form = SaleSummaryDate(initial={'date_0': datetime.date.today(),
                                        'date_1': datetime.date.today()})
    return render(request, 'sales/resources/custtomer_statement_period.html',
                  {'form': form, 'customer': customer})
