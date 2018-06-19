from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView

from cash_breakdown.models import Bank


class BankList(LoginRequiredMixin, ListView):
    model = Bank


@login_required()
@permission_required('core.add_bank', raise_exception=True)
def create_banks(request):
    """
        Add  banks
        :param request:
        :return response:
        """
    bank_formset = modelformset_factory(Bank, fields=('name',), extra=0, min_num=1)
    if request.method == 'POST':
        formset = bank_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'banks added successfully!')
            return redirect(reverse_lazy('banks'))
    else:
        formset = bank_formset(queryset=Bank.objects.none())
    return render(request, 'cash_breakdown/create_banks.html', {'formset': formset})
