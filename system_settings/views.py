from django.shortcuts import render
from system_settings import forms
from system_settings import models


# Create your views here.
def main_center_setting(request):
    settings = models.Settings.objects.latest('updated_at')
    if request.method == 'POST':
        form = forms.MainCenterForm(request.POST)
    else:
        form = forms.MainCenterForm()
    return render(request, 'system_settings/main-center.html', {'form': form})
