from django import forms


class CashExpenseDateModal(forms.Form):
    date = forms.DateField(label='Date')
