from datetime import datetime
import datetime

from django.db.models import F, Sum
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View

from sales import resources
from .render_pdf import render_to_pdf
from sales import models


def export_customers(request):
    customer_resource = resources.CustomerResource()
    dataset = customer_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customer_%s.csv"' % str(datetime.now())
    return response


class GeneratePDF(View):
    def get(self, request, day, *args, **kwargs):
        day_from_date = datetime.datetime.strptime(day, '%Y-%m-%d').date()
        date_from = datetime.datetime.combine(day_from_date, datetime.time(0, 0))
        date_to = datetime.datetime.combine(day_from_date, datetime.time(23, 59))
        particulars = models.CashReceiptParticular.objects.filter(
            cash_receipt__date__range=(date_from, date_to)).select_related('product').annotate(
            total_sum=F('price') * F('qty')
        ).order_by('-cash_receipt__date')
        total_qty = particulars.aggregate(sum=Sum('qty'))
        total_amount = particulars.aggregate(total=Sum(F('qty') * F('price')))
        template = get_template('sales/resources/cash_sale.html')
        context = {
            "particulars": particulars,
            "total_qty": total_qty,
            'total_amount': total_amount,
            'day': day_from_date
        }
        html = template.render(context)
        pdf = render_to_pdf('sales/resources/cash_sale.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "cash_sale_%s.pdf" % day
            content = "inline; filename='%s'" % filename
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % filename
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
