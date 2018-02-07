from django import forms
from django.contrib.auth.models import Group,Permission


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all())

    class Meta:
        model = Group
        fields = ('name', 'permissions')
