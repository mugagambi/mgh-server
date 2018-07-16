from django import forms
from django_select2.forms import Select2Widget

from core.models import Product
from sales import models


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


class DueDateForm(forms.Form):
    due_date = forms.DateField(label='Due Date')
    customer_number_due_date = forms.CharField(widget=forms.HiddenInput())


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
        fields = ('customer', 'product', 'qty', 'price', 'date', 'approved', 'replaced', 'reason', 'description')
        widgets = {'product': Select2Widget, 'customer': forms.HiddenInput}


class ReceiptParticularForm(forms.ModelForm):
    class Meta:
        model = models.ReceiptParticular
        fields = ('type', 'product', 'qty', 'price')
        widgets = {'product': Select2Widget}


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = models.Receipt
        fields = ('customer', 'date')
        widgets = {'customer': Select2Widget}


class ReceiptPaymentForm(forms.ModelForm):
    class Meta:
        model = models.ReceiptPayment
        fields = ['amount', 'type', 'check_number', 'mobile_number', 'transfer_code']


class TotalDiscountForm(forms.ModelForm):
    class Meta:
        model = models.CustomerTotalDiscount
        fields = ['discount']


class DiscountForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super(DiscountForm, self).__init__(**kwargs)
        self.fields['product'].disabled = True

    class Meta:
        model = models.CustomerDiscount
        fields = ['product', 'discount']


class CashReceiptPreForm(forms.Form):
    date = forms.DateTimeField()
