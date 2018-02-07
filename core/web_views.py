from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
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
