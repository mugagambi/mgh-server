from django.contrib import messages
from django.shortcuts import render, redirect
from system_settings import forms
from system_settings import models
from django.urls import reverse_lazy


# Create your views here.
def main_center_setting(request):
    settings = models.Settings.objects.all().first()
    if not settings:
        models.Settings.objects.create()
    if request.method == 'POST':
        form = forms.MainCenterForm(request.POST)
        if form.is_valid():
            main_distribution_center = form.cleaned_data['main_distribution_center']
            if settings:
                settings.main_distribution = main_distribution_center
                settings.save()
            else:
                models.Settings.objects.create(main_distribution=main_distribution_center)
            messages.success(request, 'main distribution center setting updated.')
            return redirect(reverse_lazy('main-center'))
    else:
        if models.Settings.objects.exists():
            form = forms.MainCenterForm(initial={'main_distribution_center': settings.main_distribution})
        else:
            form = forms.MainCenterForm()
    return render(request, 'system_settings/main-center.html', {'form': form})
