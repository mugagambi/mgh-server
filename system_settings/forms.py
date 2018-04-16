from django import forms
from core.models import AggregationCenter
from django.contrib.auth import get_user_model


class MainCenterForm(forms.Form):
    main_distribution_center = forms.ModelChoiceField(queryset=AggregationCenter.objects.all())


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
