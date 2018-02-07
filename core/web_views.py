from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from core import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from core import forms
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'core/group_list.html'


class GroupCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Group
    template_name = 'core/group_create_form.html'
    success_url = reverse_lazy('core:groups')
    form_class = forms.GroupForm
    success_message = 'Group created successfully'

    def get_context_data(self, **kwargs):
        permissions = Permission.objects.all()
        kwargs['permissions'] = permissions
        return super(GroupCreateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        object = form.save()
        object.permissions.set(form.cleaned_data.get('permissions'))
        return super(GroupCreateView, self).form_valid(form)


class GroupUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Group
    template_name = 'core/group_update_form.html'
    success_url = reverse_lazy('core:groups')
    form_class = forms.GroupForm
    success_message = 'Group updated successfully'

    def get_context_data(self, **kwargs):
        permissions = Permission.objects.all()
        current_permissions = self.object.permissions.all()
        kwargs['permissions'] = permissions
        kwargs['current_permissions'] = current_permissions
        return super(GroupUpdateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        object = form.save()
        object.permissions.clear()
        object.permissions.set(form.cleaned_data.get('permissions'))
        return super(GroupUpdateView, self).form_valid(form)


class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'core/group_confirm_delete.html'
    success_url = reverse_lazy('core:groups')
    success_message = 'Group removed successfully'

    def delete(self, request, *args, **kwargs):
        messages.success(request, message='Group removed successfully')
        return super(GroupDeleteView, self).delete(request)
