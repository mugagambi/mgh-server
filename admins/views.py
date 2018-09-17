from django.contrib.auth.mixins import (AccessMixin, LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

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
