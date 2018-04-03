from django import forms
from core.models import AggregationCenter


class MainCenterForm(forms.Form):
    main_center = forms.ModelChoiceField(queryset=AggregationCenter.objects.all())
