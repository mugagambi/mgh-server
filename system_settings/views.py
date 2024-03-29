from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from sales.models import BilledTogether, BilledTogetherCustomer
from system_settings import forms
from system_settings import models
from utils import main_generate_unique_id


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
@permission_required('core.add_user', raise_exception=True)
@transaction.atomic
def create_user(request):
    if request.method == 'POST':
        form = forms.UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            password = main_generate_unique_id()
            user.set_password(password)
            subject = 'Your login credentials to Meru Greens Horticulture Ltd System'
            message = 'You need a email mail client that supports html messages to read this email'
            html_message = loader.render_to_string(
                'system_settings/user_addition_email.html',
                {
                    'username': user.username,
                    'login_link': request.build_absolute_uri(reverse('sign-in')),
                    'password': password,
                    'password_link': request.build_absolute_uri(reverse('change_password'))
                }
            )
            user.email_user(subject=subject, message=message, html_message=html_message)
            user.save()
            return redirect('users')
    else:
        form = forms.UserCreationForm()
    return render(request, 'system_settings/create-users.html', {'form': form})


@login_required()
@permission_required('core.add_user', raise_exception=True)
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


@login_required()
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'system_settings/change_password.html', {
        'form': form
    })


@login_required()
@permission_required('core.add_user', raise_exception=True)
def assign_permissions(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    his_permissions = user.user_permissions.all()
    permission = Permission.objects.exclude(codename__in=(
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
    ))
    if request.method == 'POST':
        selected_permissions = request.POST.getlist('permissions[]')
        selected_permissions_objects = Permission.objects.filter(id__in=selected_permissions)
        user.user_permissions.set(selected_permissions_objects)
        return redirect('users')
    return render(request, 'system_settings/permissions.html', {'permission': permission,
                                                                'his_permission': his_permissions,
                                                                'user': user})


# todo permissions
class BilledTogetherView(LoginRequiredMixin, ListView):
    template_name = 'system_settings/billing_list.html'
    model = BilledTogether


class AddBilling(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BilledTogether
    form_class = forms.BilledTogetherForm
    template_name = 'system_settings/add-billing.html'
    success_url = reverse_lazy('billings')
    success_message = 'the billing group has been added successfully'


class UpdateBillingView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = BilledTogether
    form_class = forms.BilledTogetherForm
    template_name = 'system_settings/add-billing.html'
    success_url = reverse_lazy('billings')
    success_message = 'the billing group has been updated successfully'


class DeleteBilling(LoginRequiredMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Billing Group removed!')
        return super().post(request, *args, **kwargs)

    template_name = 'crud/delete.html'
    model = BilledTogether
    success_url = reverse_lazy('billings')


@login_required()
def billing_group_customer_list(request, billing):
    billing_group = get_object_or_404(BilledTogether, pk=billing)
    customers = BilledTogetherCustomer.objects.filter(company=billing_group)
    if request.method == 'POST':
        form = forms.BilledTogetherCustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added successfully')
            return redirect('customer_list', billing=billing_group.pk)
    else:
        form = forms.BilledTogetherCustomerForm(initial={
            'company': billing_group,
            'customer': None
        })
    return render(request, 'system_settings/billing-customers.html',
                  {'billing': billing_group,
                   'object_list': customers,
                   'form': form})


class RemoveCustomer(LoginRequiredMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Customer Removed from the group!')
        return super().post(request, *args, **kwargs)

    template_name = 'crud/delete.html'
    model = BilledTogetherCustomer

    def get_success_url(self):
        return reverse_lazy('customer_list', kwargs={'billing': self.kwargs['billing']})
