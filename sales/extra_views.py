import datetime

from django.contrib import messages
from django.db.models import F, Sum

from sales import models
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from sales import forms
from utils import generate_unique_id


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
    )
    total_qty = particulars.aggregate(sum=Sum('qty'))
    total_amount = particulars.aggregate(total=Sum(F('qty') * F('price')))
    return render(request, 'sales/sales/cash-receipt.html', {
        'particulars': particulars,
        'total_qty': total_qty,
        'total_amount': total_amount,
        'day': day_from_date
    })
