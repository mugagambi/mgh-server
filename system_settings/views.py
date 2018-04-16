import uuid

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from system_settings import forms
from system_settings import models


# Create your views here.
@login_required()
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


class SystemUsersList(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = 'system_settings/system-users-list.html'
    context_object_name = 'users'


@login_required()
def create_user(request):
    if request.method == 'POST':
        form = forms.UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            password = uuid.uuid4().hex
            print(password)
            user.set_password(password)
            user.save()
            return redirect('users')
    else:
        form = forms.UserCreationForm()
    return render(request, 'system_settings/create-users.html', {'form': form})


@login_required()
@require_http_methods(['POST'])
def deactivate_user(request):
    username = request.POST.get('username')
    option = request.POST.get('option')
    user = get_object_or_404(get_user_model(), username=username)
    if option == 'activate':
        user.is_active = True
        user.save()
        messages.success(request, 'user activated successfully.This user can'
                                  ' now log in to the system')
    elif option == 'de-activate':
        user.is_active = False
        user.save()
        messages.success(request, 'user de-activated successfully.This user can'
                                  ' not log in to the system from now until activated again')
    return redirect('users')
