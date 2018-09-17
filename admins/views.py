from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Admin
# Create your views here.
class AdminsList(LoginRequiredMixin, ListView):
    model = Admin
    template_name = 'admins/list.html'