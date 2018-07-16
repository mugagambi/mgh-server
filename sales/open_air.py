from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.utils import timezone

from sales import models
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
