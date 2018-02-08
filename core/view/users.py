from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from core.models import User


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'core/users/user_list.html'
