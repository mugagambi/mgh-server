from sales import models
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class ReturnsList(LoginRequiredMixin, ListView):
    model = models.Return
