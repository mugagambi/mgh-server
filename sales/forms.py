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
        fields = ('shop_name', 'nick_name', 'location', 'phone_number', 'email', 'notification_by', 'region')
        widgets = {'region': Select2Widget}


class OrderProductForm(forms.ModelForm):
    class Meta:
        model = models.OrderProduct
        fields = ('product', 'qty',)
        widgets = {'product': Select2Widget}


class ProductSelectionForm(forms.Form):
    product = forms.ModelChoiceField(widget=Select2Widget, queryset=Product.objects.all())


class PlaceOrderModal(forms.Form):
    date_of_delivery = forms.DateField(label='Date Of Delivery')
    customer_number = forms.CharField(widget=forms.HiddenInput())


class CustomerPriceForm(forms.ModelForm):
    class Meta:
        model = models.CustomerPrice
        fields = ('price',)


class BbfForm(forms.ModelForm):
    class Meta:
        model = models.BBF
        fields = ('amount',)


class ReturnForm(forms.ModelForm):
    class Meta:
        model = models.Return
        fields = ('customer', 'product', 'qty', 'price', 'reason', 'description')
        widgets = {'product': Select2Widget, 'customer': forms.HiddenInput}


class ReceiptParticularForm(forms.ModelForm):
    class Meta:
        model = models.ReceiptParticular
        fields = ('type', 'product', 'qty', 'price', 'discount')
        widgets = {'product': Select2Widget}


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = models.Receipt
        fields = ('customer', 'date')
        widgets = {'customer': Select2Widget}
