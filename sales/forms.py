from django import forms
from sales import models


class RegionForm(forms.ModelForm):
    class Meta:
        model = models.Region
        fields = ('name',)
