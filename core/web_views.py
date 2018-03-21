from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView

from core import models
from django.views.generic.list import ListView


class CentersList(ListView):
    model = models.AggregationCenter
    template_name = 'core/centers/index.html'


def create_centers(request):
    center_formset = modelformset_factory(models.AggregationCenter, exclude=('is_active',), max_num=10)
    if request.method == 'POST':
        formset = center_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'centers added successfully!')
            return redirect(reverse_lazy('centers-list'))
    else:
        formset = center_formset(queryset=models.AggregationCenter.objects.none())
        return render(request, 'core/centers/create.html', {'formset': formset})


class UpdateCenter(SuccessMessageMixin, UpdateView):
    model = models.AggregationCenter
    fields = ['name', 'location']
    template_name = 'sales/regions/update.html'
    success_url = reverse_lazy('centers-list')
    success_message = 'Center updated successfully'


class DeleteCenter(DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'center removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'core/centers/delete.html'
    model = models.AggregationCenter
    success_url = reverse_lazy('centers-list')
