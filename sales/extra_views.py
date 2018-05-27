from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from core.models import Product
from sales import forms
from sales import models
from utils import generate_unique_id, main_generate_unique_id


# todo add the right permissions
class ReturnsList(LoginRequiredMixin, ListView):
    model = models.Return
    template_name = 'sales/returns/returns-list.html'
    context_object_name = 'returns'
    queryset = models.Return.objects.select_related('product', 'customer', 'approved_by').annotate(
        credit_note=F('qty') * F('price'))
    paginate_by = 50


# todo add the right permissions
@login_required()
def record_return(request, customer):
    customer = get_object_or_404(models.Customer, pk=customer)
    if request.method == 'POST':
        form = forms.ReturnForm(request.POST)
        if form.is_valid():
            returns = form.save(commit=False)
            returns.number = generate_unique_id(request.user.id)
            returns.approved_by = request.user
            returns.save()
            messages.success(request, 'Return recorded')
            return redirect('returns')
    else:
        form = forms.ReturnForm(initial={'customer': customer})
    return render(request, 'sales/returns/create_returns.html', {'form': form, 'customer': customer})


# todo add required permissions
@login_required()
def cash_receipt(request, pk):
    receipt = get_object_or_404(models.CashReceipt, pk=pk)
    particulars = models.CashReceiptParticular.objects.filter(cash_receipt=receipt).select_related('product'). \
        annotate(total_sum=F('price') * F('qty')).order_by('-cash_receipt__date')
    total_qty = particulars.aggregate(sum=Sum('qty'))
    total_amount = particulars.aggregate(total=Sum(F('qty') * F('price')))
    return render(request, 'sales/sales/cash-receipt.html', {
        'particulars': particulars,
        'total_qty': total_qty,
        'total_amount': total_amount,
        'receipt': receipt
    })


@login_required()
@permission_required('sales.add_receiptparticular', raise_exception=True)
def add_receipt_particular(request, pk):
    receipt = get_object_or_404(models.Receipt, pk=pk)
    product_ids = [receipt.product.id for receipt in receipt.receiptparticular_set.all()]
    products = Product.objects.exclude(pk__in=product_ids)
    if request.method == 'POST':
        form = forms.ReceiptParticularForm(request.POST)
        if form.is_valid():
            particular = form.save(commit=False)
            particular.receipt = receipt
            particular.save()
            messages.success(request, 'Item added successfully.Totals have been re-calculated')
            return redirect('sale-receipt', pk=receipt.pk)
    else:
        form = forms.ReceiptParticularForm()
        form.fields['product'].queryset = products
    return render(request, 'sales/sales/add-receipt-particular.html', {'form': form, 'receipt': receipt})


@login_required()
@permission_required('sales.add_receipt', raise_exception=True)
def add_receipt(request):
    if request.method == 'POST':
        form = forms.ReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.number = generate_unique_id(request.user.id)
            receipt.served_by = request.user
            receipt.save()
            messages.success(request, 'Receipt added successfully')
            return redirect('sale-receipt', pk=receipt.number)
    else:
        form = forms.ReceiptForm()
    return render(request, 'sales/sales/add_receipt.html', {'form': form})


# todo add the required permissions
@login_required()
def trade_debtors(request):
    debtors = models.CustomerAccountBalance.objects.filter(~Q(amount=0.0)).order_by('customer__shop_name')
    credit_total = debtors.filter(amount__gt=Decimal('0.0')).aggregate(total=Sum('amount'))
    debit_total = debtors.filter(amount__lt=Decimal('0.0')).aggregate(total=Sum('amount'))
    return render(request, 'sales/sales/customer_accounts.html', {
        'debtors': debtors,
        'credit_total': credit_total,
        'debit_total': debit_total
    })


# todo add the right permissions
@login_required()
def customer_statement(request, customer):
    customer = get_object_or_404(models.Customer, pk=customer)
    account = models.CustomerAccount.objects.select_related('customer', 'receipt', 'returns').filter(
        customer=customer).order_by('-date')
    receipt_purchases_total = account.filter(type='P').values('receipt', 'date').annotate(Sum('amount'))
    receipt_payments_total = account.filter(type='A').values('receipt', 'date').annotate(Sum('amount'))
    account = account.exclude(type__in=['P', 'A'])
    final_account = []
    for total in receipt_purchases_total:
        if not receipt_payments_total.exists():
            final_account.append({
                'purchase': total['amount__sum'],
                'payment': '-',
                'receipt_id': total['receipt'],
                'return_id': None,
                'date': total['date'],
                'customer': None
            })
            continue
        for payment in receipt_payments_total:
            if total['receipt'] == payment['receipt']:
                final_account.append({
                    'purchase': total['amount__sum'],
                    'payment': payment['amount__sum'],
                    'receipt_id': payment['receipt'],
                    'return_id': None,
                    'date': payment['date'],
                    'customer': None
                })
                continue
    for acc in account:
        if acc.type == 'R':
            final_account.append({
                'purchase': '-',
                'payment': str(acc.amount) + '-return',
                'receipt_id': None,
                'return_id': acc.returns.number,
                'date': acc.date,
                'customer': None
            })
            continue
        if acc.type == 'D':
            final_account.append({
                'purchase': '-',
                'payment': str(acc.amount) + ' -deposit',
                'receipt_id': None,
                'return_id': None,
                'date': acc.date,
                'customer': acc.customer.number
            })
            continue
        if acc.type == 'B':
            final_account.append({
                'purchase': '-',
                'payment': str(acc.amount) + ' -BBF',
                'receipt_id': None,
                'return_id': None,
                'date': acc.date,
                'customer': None
            })
        continue
    try:
        balance = models.CustomerAccountBalance.objects.get(customer=customer)
    except models.CustomerAccountBalance.DoesNotExist:
        balance = None
    return render(request, 'sales/sales/customer_statement.html',
                  {'customer': customer, 'account': final_account, 'balance': balance})


@login_required()
@permission_required('sales.change_receiptparticular')
def update_particular(request, item):
    item = get_object_or_404(models.ReceiptParticular, pk=item)
    old_total = item.qty * item.price
    if request.method == 'POST':
        form = forms.ReceiptParticularForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            new_total = item.qty * item.price
            diff = new_total - old_total
            models.CustomerAccount.objects.create(number=main_generate_unique_id(),
                                                  customer=item.receipt.customer,
                                                  amount=-diff,
                                                  date=item.receipt.date,
                                                  type='P',
                                                  receipt=item.receipt)
            messages.success(request, 'Item updated successfully')
            return redirect('sale-receipt', pk=item.receipt.number)
    else:
        form = forms.ReceiptParticularForm(instance=item)
    return render(request, 'sales/sales/add-receipt-particular.html', {'form': form, 'item': item})


# todo remove all the particulars and payments from the account
@login_required()
@permission_required('sales.delete_receipt')
def delete_receipt(request, pk):
    """
    on deleting a receipt, remove the total amount of in particulars in the customer account.Do this by adding an amount
    with equal and opposite amount to the particular.
    That wouldn't work also because the receipt will be deleted and it will be null.
    Another approach is to ignore all the null values and only show the ones with the receipts.
    These null values will affect the final account balance accordingly.
    And this is the desired behaviour.
    todo work on this approach. and do the same with removing receipt particular and a specific payment.
    :param request:
    :param pk:
    :return:
    """
    pass


@login_required()
@permission_required('sales.add_receiptpayment')
def add_payment(request, receipt):
    receipt = get_object_or_404(models.Receipt, pk=receipt)
    if request.method == 'POST':
        form = forms.ReceiptPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.receipt = receipt
            payment.save()
            messages.success(request, 'payment added successfully')
            return redirect('sale-receipt', pk=receipt.number)
    else:
        form = forms.ReceiptPaymentForm()
    return render(request, 'sales/sales/receipt_payment.html', {'form': form, 'receipt': receipt})


@login_required()
@permission_required('sales.change_receiptpayment')
def update_payment(request, receipt, payment):
    receipt = get_object_or_404(models.Receipt, pk=receipt)
    payment = get_object_or_404(models.ReceiptPayment, receipt=receipt, pk=payment)
    old_amount = payment.amount
    if request.method == 'POST':
        form = forms.ReceiptPaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save()
            new_amount = payment.amount
            diff = new_amount - old_amount
            if payment.type == 1:
                type = 'Q'
                cheque_number = payment.check_number
                transaction_id = ''
                phone_number = ''
            elif payment.type == 2:
                type = 'M'
                cheque_number = ''
                transaction_id = payment.transaction_id
                phone_number = payment.mobile_number
            elif payment.type == 3:
                type = 'C'
                cheque_number = ''
                transaction_id = ''
                phone_number = ''
            elif payment.type == 5:
                type = 'B'
                cheque_number = ''
                transaction_id = ''
                phone_number = ''
            else:
                type = ''
                cheque_number = ''
                transaction_id = ''
                phone_number = ''
            if payment.type != 4:
                models.CustomerAccount.objects.create(number=main_generate_unique_id(),
                                                      customer=payment.receipt.customer,
                                                      amount=diff,
                                                      date=payment.receipt.date,
                                                      type='A',
                                                      via=type,
                                                      receipt=payment.receipt,
                                                      cheque_number=cheque_number,
                                                      transaction_id=transaction_id,
                                                      phone_number=phone_number)
            messages.success(request, 'Payment updated and the customer account has been updated updated')
            return redirect('sale-receipt', pk=receipt.number)
    else:
        form = forms.ReceiptPaymentForm(instance=payment)
    return render(request, 'sales/sales/receipt_payment.html', {'form': form,
                                                                'receipt': receipt,
                                                                'payment': payment})


# todo add the required the permissions
@login_required()
def return_details(request, pk):
    returns = get_object_or_404(models.Return, pk=pk)
    return render(request, 'sales/returns/return.html', {'return': returns})
