from django.shortcuts import redirect, render
from django.views.generic import TemplateView, ListView
from sales import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.forms import modelformset_factory


class OrdersView(TemplateView):
    template_name = 'sales/orders.html'


class RegionList(LoginRequiredMixin, ListView):
    model = models.Region
    template_name = 'sales/regions/index.html'


def create_regions(request):
    region_formset = modelformset_factory(models.Region, fields=('name',), max_num=10)
    if request.method == 'POST':
        formset = region_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'regions added successfully!')
            return redirect(reverse_lazy('regions'))
    else:
        formset = region_formset(queryset=models.Region.objects.none())
        return render(request, 'sales/regions/create.html', {'formset': formset})


class CreateRegion(SuccessMessageMixin, CreateView):
    model = models.Region
    fields = ['name']
    template_name = 'sales/regions/create.html'
    success_url = reverse_lazy('regions')
    success_message = 'region created successfully'


class UpdateRegion(SuccessMessageMixin, UpdateView):
    model = models.Region
    fields = ['name']
    template_name = 'sales/regions/update.html'
    success_url = reverse_lazy('regions')
    success_message = 'region updated successfully'


class DeleteRegion(DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'region removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'sales/regions/delete.html'
    model = models.Region
    success_url = reverse_lazy('regions')
