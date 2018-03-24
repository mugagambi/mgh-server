from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView
from django.views.generic.list import ListView
from django_select2.forms import Select2Widget

from core import models


class CentersList(LoginRequiredMixin, ListView):
    model = models.AggregationCenter
    template_name = 'core/centers/index.html'


@login_required()
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


class UpdateCenter(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.AggregationCenter
    fields = ['name', 'location']
    template_name = 'sales/regions/update.html'
    success_url = reverse_lazy('centers-list')
    success_message = 'Center updated successfully'


class DeleteCenter(LoginRequiredMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'center removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'core/centers/delete.html'
    model = models.AggregationCenter
    success_url = reverse_lazy('centers-list')


class ProductList(LoginRequiredMixin, ListView):
    model = models.Product
    template_name = 'core/products/index.html'


@login_required()
def create_product(request):
    product_formset = modelformset_factory(models.Product, fields=('name',), max_num=10)
    if request.method == 'POST':
        formset = product_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Products added successfully!')
            return redirect(reverse_lazy('products-list'))
    else:
        formset = product_formset(queryset=models.Product.objects.none())
    return render(request, 'crud/formset-create.html', {'formset': formset,
                                                        'create_name': 'Products',
                                                        'create_sub_name': 'product'})


class UpdateProduct(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Product
    fields = ['name']
    template_name = 'crud/update.html'
    success_url = reverse_lazy('products-list')
    success_message = 'Product updated successfully'


class DeleteProduct(LoginRequiredMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'product removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'crud/delete.html'
    model = models.Product
    success_url = reverse_lazy('products-list')


@login_required()
def product_availability(request, center):
    """used to indicate amount of products for sale in a center"""
    center_product_formset = modelformset_factory(models.AggregationCenterProduct, fields=('product', 'qty'),
                                                  widgets={'product': Select2Widget}, extra=10, min_num=1,
                                                  can_delete=True)
    center = models.AggregationCenter.objects.get(pk=center)
    dt = datetime.now()
    if request.method == 'POST':
        formset = center_product_formset(request.POST)
        if formset.is_valid():
            products = formset.save(commit=False)
            for product in products:
                product.aggregation_center = center
                product.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, 'Product availability in %s updated successfully!' % center.name)
            return redirect(reverse_lazy('centers-list'))
    else:
        formset = center_product_formset(
            queryset=models.AggregationCenterProduct.objects.select_related('product').filter(
                aggregation_center=center, date=datetime.now()))
    return render(request, 'crud/formset-create.html', {'formset': formset,
                                                        "center": center,
                                                        'create_name': center.name + ' product availability for ' + dt.strftime(
                                                            '%a %B %d, %Y'),
                                                        'create_sub_name': 'quantities'})
