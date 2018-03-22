from django import forms
from django_select2.forms import Select2Widget

from sales import models


class RegionForm(forms.ModelForm):
    class Meta:
        model = models.Region
        fields = ('name',)


class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ('shop_name', 'nick_name', 'location', 'phone_number', 'email', 'region')
        widgets = {'region': Select2Widget}
