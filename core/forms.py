from django import forms
from core import models


class AvailableProductForm(forms.ModelForm):
    class Meta:
        model = models.AggregationCenterProduct
        fields = ('qty',)
