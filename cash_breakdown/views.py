from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.views.generic import ListView

from cash_breakdown.models import Bank


class BankList(LoginRequiredMixin, ListView):
    model = Bank
