from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# Create your views here.
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView

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


class UpdateBank(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Bank
    fields = ('name',)
    permission_required = 'core.change_bank'
    success_message = 'Bank details have been updated'
    success_url = reverse_lazy('banks')
    template_name = 'cash_breakdown/update_bank.html'


class DeleteBank(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, 'Bank removed successfully')
        return super(DeleteBank, self).delete(request, *args, **kwargs)

    template_name = 'crud/delete.html'
    model = Bank
    success_url = reverse_lazy('banks')
    permission_required = 'bank.delete_bank'
