from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum, F
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, UpdateView, DeleteView

from cash_breakdown.models import Bank, CashDeposit, CashExpense
from .form import CashExpenseDateModal


class BankList(LoginRequiredMixin, ListView):
    model = Bank


@login_required()
@permission_required('cash_breakdown.add_bank', raise_exception=True)
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
    permission_required = 'cash_breakdown.change_bank'
    success_message = 'Bank details have been updated'
    success_url = reverse_lazy('banks')
    template_name = 'cash_breakdown/update_bank.html'


class DeleteBank(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.cashdeposit_set.exists():
            messages.error(request, 'You can\'t remove this bank because it already has deposits')
            return redirect('banks')
        messages.success(request, 'Bank removed successfully')
        return super(DeleteBank, self).delete(request, *args, **kwargs)

    template_name = 'crud/delete.html'
    model = Bank
    success_url = reverse_lazy('banks')
    permission_required = 'cash_breakdown.delete_bank'


class CashDepositList(LoginRequiredMixin, ListView):
    model = CashDeposit
    template_name = 'cash_breakdown/cash_deposit_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(CashDepositList, self).get_context_data(object_list=None, **kwargs)
        ctx['banks'] = Bank.objects.all()
        if self.request.GET.get('bank'):
            ctx['bank_id'] = int(self.request.GET.get('bank'))
        return ctx

    def get_queryset(self):
        bank = self.request.GET.get('bank', None)
        date = self.request.GET.get('date', None)
        if bank and date:
            date = parse_date(date)
            return CashDeposit.objects.select_related('bank').filter(bank_id=bank, date=date).order_by('-date')
        elif bank:
            return CashDeposit.objects.select_related('bank').filter(bank_id=bank).order_by('-date')
        elif date:
            date = parse_date(date)
            return CashDeposit.objects.select_related('bank').filter(date=date).order_by('-date')
        return CashDeposit.objects.select_related('bank').all().order_by('-date')


@login_required()
@permission_required('cash_breakdown.add_cashdeposit', raise_exception=True)
def add_deposits(request):
    """
        Add  banks
        :param request:
        :return response:
        """
    deposit_formset = modelformset_factory(CashDeposit, fields=('bank', 'amount', 'date'), extra=0, min_num=1)
    if request.method == 'POST':
        formset = deposit_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Cash deposits added!')
            return redirect(reverse_lazy('cash_deposits'))
    else:
        formset = deposit_formset(queryset=CashDeposit.objects.none())
    return render(request, 'cash_breakdown/add_cash_deposit.html', {'formset': formset})


class UpdateCashDeposit(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CashDeposit
    fields = ('bank', 'amount', 'date')
    permission_required = 'cash_breakdown.change_cashdeposit'
    success_message = 'Cash Deposit details have been updated'
    success_url = reverse_lazy('cash_deposits')
    template_name = 'cash_breakdown/cash_deposit_update.html'


class CashExpenseList(LoginRequiredMixin, ListView):
    model = CashExpense
    template_name = 'cash_breakdown/cash_expense_list.html'
    queryset = CashExpense.objects.values('date').annotate(total_amount=Sum('amount'), narration=F('expense'))

    def get_context_data(self, *, object_list=None, **kwargs):
        form = CashExpenseDateModal(initial={'date': now()})
        ctx = super(CashExpenseList, self).get_context_data(object_list=None, **kwargs)
        ctx['form'] = form
        return ctx


@login_required()
@require_http_methods(['POST'])
def handle_cash_expense_date(request):
    form = CashExpenseDateModal(request.POST)
    if form.is_valid():
        date = form.cleaned_data['date']
        return redirect(reverse('create_cash_expense', kwargs={'date': str(date)}))
    messages.error(request, 'To proceed you need to select date')
    return redirect('cash_expenses')


@login_required()
@permission_required('cash_breakdown.add_cashexpense', raise_exception=True)
def create_expenses(request, date):
    """
        Add  cash expense
        :param request:
        :return response:
        """
    date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
    expense_formset = modelformset_factory(CashExpense, fields=('amount', 'narration'), extra=0, min_num=1,
                                           widgets={'narration': forms.Textarea(attrs={'rows': 2})})
    if request.method == 'POST':
        formset = expense_formset(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.date = date
                instance.save()
            messages.success(request, 'Expenses added successfully!')
            return redirect(reverse_lazy('cash_expenses'))
    else:
        formset = expense_formset(queryset=CashExpense.objects.none())
    return render(request, 'cash_breakdown/add_expenses.html', {'formset': formset})

