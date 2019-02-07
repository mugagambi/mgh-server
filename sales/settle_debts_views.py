from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required,permission_required
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods

from .models import CustomerDeposit, ReceiptPayment, Receipt


@login_required()
@permission_required('sales.add_receiptpayment')
def settle_debt(request, deposit):
    deposit = get_object_or_404(CustomerDeposit, pk=deposit)
    invoices = ReceiptPayment.objects.filter(receipt__customer=deposit.customer,
                                             type=4)
    receipt_ids = [invoice.receipt.pk for invoice in invoices]
    receipts_qs = Receipt.objects.filter(number__in=receipt_ids, settled=False)
    receipts = receipts_qs.annotate(amount=Sum('receiptparticular__total')).values('number', 'date',
                                                                                   'balance', 'settled')
    total_required = receipts_qs.aggregate(amount=Sum('balance'))
    return render(request, 'sales/settle-deposits/settling-invoices.html',
                  {'deposit': deposit, 'receipts': receipts, 'total_required': total_required})


@login_required()
@permission_required('sales.change_customerdeposit')
@require_http_methods(['POST'])
@transaction.atomic
def settle_invoice_debt(request):
    deposit = request.POST.get('deposit', None)
    invoice = request.POST.get('invoice', None)
    if not deposit:
        messages.error(request, 'You need a deposit to settle debt')
        return redirect('customer_list')
    elif not invoice:
        messages.error(request, 'You need an invoice to settle debt')
        return redirect('customer_list')
    else:
        deposit = CustomerDeposit.objects.get(pk=deposit)
        invoice = Receipt.objects.get(pk=invoice)
        if deposit.remaining_amount >= invoice.balance:
            deposit.remaining_amount = deposit.remaining_amount - invoice.balance
            deposit.save()
            invoice.balance = invoice.balance - invoice.balance
            invoice.settled = True
            invoice.save()
            messages.success(request, 'Invoice settled successfully')
        elif invoice.balance > deposit.remaining_amount > Decimal('0.00'):
            old_value = deposit.remaining_amount
            deposit.remaining_amount = deposit.remaining_amount - deposit.remaining_amount
            deposit.save()
            invoice.balance = invoice.balance - old_value
            invoice.save()
            messages.success(request, 'The action was successful, but the whole invoice debt was not settled '
                                      'and %s is still remaining' % str(invoice.balance))
        else:
            messages.success(request, 'The deposit does not have enough remaining amount to settle the invoice balance')
        return redirect('settle_debt_invoices', deposit=deposit.pk)
