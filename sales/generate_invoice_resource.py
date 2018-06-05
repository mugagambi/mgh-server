from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone

from sales.models import Customer, ReceiptPayment, ReceiptParticular, Receipt
from sales.render_pdf import render_to_pdf


@login_required()
def generate_invoice(request, customer, due_date):
    customer = Customer.objects.get(pk=customer)
    due_date = timezone.datetime.strptime(due_date, '%Y-%m-%d').date()
    payments = ReceiptPayment.objects.filter(type=4, receipt__customer=customer)
    receipt_ids = [payment.receipt.pk for payment in payments]
    particulars = ReceiptParticular.objects.filter(receipt__pk__in=receipt_ids)
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
    pdf = render_to_pdf('sales/resources/generate_invoice.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "%s_invoice_on_%s" % (customer.shop_name, str(today))
        content = "inline; filename='%s'" % filename
        download = request.GET.get("download")
        if download:
            content = "attachment; filename='%s'" % filename
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")
