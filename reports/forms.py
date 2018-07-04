from django import forms
from django_select2.forms import Select2Widget

from core.models import Product
from sales.models import Customer


class SaleSummaryDate(forms.Form):
    date_0 = forms.DateField(label='From')
    date_1 = forms.DateField(label='To')


class ProductCustomer(forms.Form):
    date_0 = forms.DateField(label='From')
    date_1 = forms.DateField(label='To')
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=Select2Widget)


class CustomerPerformance(forms.Form):
    date_0 = forms.DateField(label='From')
    date_1 = forms.DateField(label='To')
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=Select2Widget)
