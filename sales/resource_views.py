import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.views import View

from reports.forms import SaleSummaryDate
from sales import models
from sales import resources
from . import tasks
from .render_pdf import render_to_pdf


# todo add the right permissions
@login_required()
def export_customers(request):
    customer_resource = resources.CustomerResource()
    dataset = customer_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customer_%s.csv"' % str(datetime.now())
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
    tasks.export_customer_sales.delay(date_0, date_1)
    messages.success(request, 'The system is exporting the pdf! Wait a moment and refresh this page.')
    return redirect('invoices')
