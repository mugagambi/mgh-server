from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

from sales.models import Customer, ReceiptPayment, ReceiptParticular, Receipt


@login_required()
def generate_invoice(request, customer, due_date):
    customer = Customer.objects.get(pk=customer)
    due_date = timezone.datetime.strptime(due_date, '%Y-%m-%d').date()
    payments = ReceiptPayment.objects.filter(type=4, receipt__customer=customer)
    receipt_ids = [payment.receipt.pk for payment in payments]
    particulars = ReceiptParticular.objects.filter(receipt__pk__in=receipt_ids, receipt__settled=False)
    total_amount = particulars.aggregate(total=Sum('total'))
    receipt_balances = Receipt.objects.filter(pk__in=receipt_ids).aggregate(total=Sum('balance'))
    today = timezone.datetime.today()
    has_discount = customer.customerdiscount_set.exists()
    context = {
        'customer': customer,
        'due_date': due_date,
        'particulars': particulars,
        'total_amount': total_amount,
        'receipt_balances': receipt_balances,
        'has_discount': has_discount,
        'today': today
    }
    invoice_string = render_to_string('sales/resources/generate_invoice.html', context)
    html = HTML(string=invoice_string)
    html.write_pdf(target='/tmp/{}_{}_invoice.pdf'.format(today.strftime('%Y-%m-%d'), customer.shop_name))
    fs = FileSystemStorage('/tmp')
    with fs.open('{}_{}_invoice.pdf'.format(today.strftime('%Y-%m-%d'), customer.shop_name)) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = "inline; filename='{}_{}_invoice.pdf'".format(today.strftime('%Y-%m-%d'),
                                                                                        customer.shop_name)
        return response
