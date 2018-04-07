from django import forms


class SaleSummaryDate(forms.Form):
    date_0 = forms.DateField(label='From')
    date_1 = forms.DateField(label='To')
