import datetime
from io import BytesIO

from celery import shared_task
from django.db.models import Sum
from django.template.loader import get_template
from xhtml2pdf import pisa

from sales import models


@shared_task()
def export_customer_sales(date_0, date_1):
    date_0 = datetime.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = datetime.datetime.combine(date_0, datetime.time(0, 0))
    date_1_datetime = datetime.datetime.combine(date_1, datetime.time(23, 59))
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
    template = get_template('sales/resources/customer_sale_export.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        pdf = result.getvalue()
        with open('pdf_exports/customer_sales_from_{}_to_{}.pdf'.format(date_0, date_1), 'w+b') as w:
            w.write(pdf)
            return 'pdf_exports/customer_sales_from_{}_to_{}.pdf'.format(date_0, date_1)
