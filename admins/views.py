from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import (AccessMixin, LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .models import Admin

# Create your views here.


class AdminsList(LoginRequiredMixin, ListView):
    model = Admin
    template_name = 'admins/list.html'


class CreateAdmin(LoginRequiredMixin, PermissionRequiredMixin, AccessMixin, SuccessMessageMixin, CreateView):
    permission_denied_message = 'You don\'t have access to this page.'
    permission_required = 'admins.add_admin'
    raise_exception = True
    model = Admin
    fields = ('email',)
    success_url = reverse_lazy('admin_list')
    success_message = 'Admin added successfully'
    template_name = 'admins/create.html'


class UpdateAdmin(LoginRequiredMixin, PermissionRequiredMixin, AccessMixin, SuccessMessageMixin, UpdateView):
    permission_denied_message = 'You don\'t have access to this page.'
    permission_required = 'admins.change_admin'
    raise_exception = True
    model = Admin
    fields = ('email',)
    queryset = Admin.objects.all()
    success_url = reverse_lazy('admin_list')
    success_message = 'Admin update successfully'
    template_name = 'admins/create.html'


@login_required()
@permission_required('admins.delete_admin', raise_exception=True)
def remove_admin(request, pk):
    admin = get_object_or_404(Admin, pk=pk)
    admin.delete()
    messages.success(request, 'Admin removed successfully')
    return redirect('admin_list')
