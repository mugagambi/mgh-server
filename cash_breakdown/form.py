from django import forms

from cash_breakdown.models import CashExpense


class CashExpenseDateModal(forms.Form):
    date = forms.DateField(label='Date')


class CashExpenseForm(forms.ModelForm):
    class Meta:
        model = CashExpense
        fields = ('amount', 'narration')
