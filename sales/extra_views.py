import datetime
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from core.models import Product
from sales import forms
from sales import models
from utils import generate_unique_id, main_generate_unique_id


class ReturnsList(LoginRequiredMixin, ListView):
    model = models.Return
    template_name = 'sales/returns/returns-list.html'
    context_object_name = 'returns'
    queryset = models.Return.objects.annotate(credit_note=F('qty') * F('price'))
    paginate_by = 50


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


@login_required()
def cash_receipt(request, day):
    day_from_date = datetime.datetime.strptime(day, '%Y-%m-%d').date()
    date_from = datetime.datetime.combine(day_from_date, datetime.time(0, 0))
    date_to = datetime.datetime.combine(day_from_date, datetime.time(23, 59))
    particulars = models.CashReceiptParticular.objects.filter(
        cash_receipt__date__range=(date_from, date_to)).select_related('product').annotate(
        total_sum=F('price') * F('qty')
    ).order_by('-cash_receipt__date')
    total_qty = particulars.aggregate(sum=Sum('qty'))
    total_amount = particulars.aggregate(total=Sum(F('qty') * F('price')))
    return render(request, 'sales/sales/cash-receipt.html', {
        'particulars': particulars,
        'total_qty': total_qty,
        'total_amount': total_amount,
        'day': day_from_date
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


@login_required()
def trade_debtors(request):
    debtors = models.CustomerAccountBalance.objects.all().order_by('customer__shop_name')
    credit_total = debtors.filter(amount__gt=Decimal('0.0')).aggregate(total=Sum('amount'))
    debit_total = debtors.filter(amount__lt=Decimal('0.0')).aggregate(total=Sum('amount'))
    return render(request, 'sales/sales/customer_accounts.html', {
        'debtors': debtors,
        'credit_total': credit_total,
        'debit_total': debit_total
    })


@login_required()
def customer_statement(request, customer):
    customer = get_object_or_404(models.Customer, pk=customer)
    account = models.CustomerAccount.objects.filter(customer=customer)
    paginator = Paginator(account, 50)
    page = request.GET.get('page', 1)
    try:
        account = paginator.page(page)
    except PageNotAnInteger:
        account = paginator.page(1)
    except EmptyPage:
        account = paginator.page(paginator.num_pages)
    try:
        balance = models.CustomerAccountBalance.objects.get(customer=customer)
    except models.CustomerAccountBalance.DoesNotExist:
        balance = None
    return render(request, 'sales/sales/customer_statement.html',
                  {'customer': customer, 'account': account, 'balance': balance,
                   'paginator': paginator})


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


@login_required()
@permission_required('sales.delete_receipt')
def delete_receipt(request, pk):
    pass
