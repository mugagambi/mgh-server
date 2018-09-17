from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from sales import models
from sales.forms import CashParticularForm
from utils import generate_unique_id


@login_required()
@permission_required('sales.add_cashreceiptparticular', raise_exception=True)
def add_cash_receipt_particulars(request, date):
    date = timezone.datetime.strptime(date, '%Y-%m-%d %H:%M')
    cash_form_set = modelformset_factory(models.CashReceiptParticular, fields=('product', 'qty', 'price'), min_num=1,
                                         extra=0)
    if request.method == 'POST':
        formset = cash_form_set(request.POST)
        if formset.is_valid():
            receipt = models.CashReceipt.objects.create(number=generate_unique_id(request.user.id), date=date)
            instances = formset.save(commit=False)
            for instance in instances:
                instance.cash_receipt = receipt
                instances.save()
                messages.success(request, 'Cash receipt items added successfully')
                return redirect('cash-sales')
    else:
        formset = cash_form_set(queryset=models.CashReceiptParticular.objects.none())
    return render(request, 'sales/sales/add-cash-sale.html', {'formset': formset})


@login_required()
@permission_required('sales.change_cashreceiptparticular', raise_exception=True)
def update_open_air_sale(request, pk):
    sale = get_object_or_404(models.CashReceiptParticular, pk=pk)
    if request.method == 'POST':
        form = CashParticularForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'open air market sale updated successfully')
            return redirect('cash-receipt', date=sale.cash_receipt.date.strftime("%Y-%m-%d"))
    else:
        form = CashParticularForm(instance=sale)
    return render(request, 'sales/sales/open_air_update.html', {'form': form, 'sale': sale})
