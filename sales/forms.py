from django import forms
from django_select2.forms import Select2Widget

from sales import models
from core.models import Product


class RegionForm(forms.ModelForm):
    class Meta:
        model = models.Region
        fields = ('name',)


class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ('shop_name', 'nick_name', 'location', 'phone_number', 'email', 'region')
        widgets = {'region': Select2Widget}


class OrderProductForm(forms.ModelForm):
    def __init__(self, customer, *args, **kwargs):
        super(OrderProductForm, self).__init__(*args, **kwargs)
        self.fields['price'].queryset = models.CustomerPrice.objects.filter(customer=customer)
        self.fields['discount'].queryset = models.CustomerDiscount.objects.filter(customer=customer)

    class Meta:
        model = models.OrderProduct
        fields = ('discount', 'price', 'qty', 'product')
        widgets = {'product': Select2Widget,
                   'price': Select2Widget,
                   'discount': Select2Widget}


class ProductSelectionForm(forms.Form):
    product = forms.ChoiceField(widget=Select2Widget, choices=Product.objects.values_list('id', 'name').all())
