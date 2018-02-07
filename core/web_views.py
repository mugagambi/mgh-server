from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from core import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from core import forms


class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'core/group_list.html'


class GroupCreateView(CreateView):
    model = Group
    template_name = 'core/group_create_form.html'
    success_url = '/users/groups'
    form_class = forms.GroupForm

    def get_context_data(self, **kwargs):
        permissions = Permission.objects.all()
        kwargs['permissions'] = permissions
        return super(GroupCreateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        object = form.save()
        object.permissions.set(form.cleaned_data.get('permissions'))
        return super(GroupCreateView, self).form_valid(form)


class GroupUpdateView(UpdateView):
    model = Group
    template_name = 'core/group_update_form.html'
    success_url = '/users/groups'
    form_class = forms.GroupForm

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
