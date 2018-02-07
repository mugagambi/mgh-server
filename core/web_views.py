from django.views.generic.list import ListView
from core import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.mixins import LoginRequiredMixin


class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'core/group_list.html'
