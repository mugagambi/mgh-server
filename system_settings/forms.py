from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django_select2.forms import Select2Widget

from core.models import AggregationCenter
from sales.models import BilledTogether, BilledTogetherCustomer


class MainCenterForm(forms.Form):
    main_distribution_center = forms.ModelChoiceField(queryset=AggregationCenter.objects.all())


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')


class PermissionForm(forms.Form):
    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.exclude(codename__in=(
        # Has no admin interface:
        'add_permission',
        'change_permission',
        'delete_permission',
        'delete_church',
        'add_church',

        'add_contenttype',
        'change_contenttype',
        'delete_contenttype',

        'add_session',
        'delete_session',
        'change_session',

        # django.contrib.admin
        'add_logentry',
        'change_logentry',
        'delete_logentry',
    )))


class BilledTogetherForm(forms.ModelForm):
    class Meta:
        model = BilledTogether
        fields = ['name', 'phone', 'email', 'box']


class BilledTogetherCustomerForm(forms.ModelForm):
    class Meta:
        model = BilledTogetherCustomer
        fields = ['customer', 'company']
        widgets = {'company': forms.HiddenInput(),
                   'customer': Select2Widget}
