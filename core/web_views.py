from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import modelformset_factory
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView
from django.views.generic.list import ListView
from django_select2.forms import Select2Widget

from core import forms
from core import models


# TODO add the right permissions
class CentersList(LoginRequiredMixin, ListView):
    """
    A list of all the centers
    """
    model = models.AggregationCenter
    template_name = 'core/centers/index.html'


@login_required()
@permission_required('core.add_aggregation_center', raise_exception=True)
def create_centers(request):
    """
    Add  a new center
    :param request:
    :return response:
    """
    center_formset = modelformset_factory(models.AggregationCenter, exclude=('is_active',), extra=0, min_num=1)
    if request.method == 'POST':
        formset = center_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'centers added successfully!')
            return redirect(reverse_lazy('centers-list'))
    else:
        formset = center_formset(queryset=models.AggregationCenter.objects.none())
    return render(request, 'core/centers/create.html', {'formset': formset})


class UpdateCenter(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Update a certain center
    """
    model = models.AggregationCenter
    permission_required = 'core.change_aggregationcenter'
    fields = ['name', 'location']
    template_name = 'sales/regions/update.html'
    success_url = reverse_lazy('centers-list')
    success_message = 'Center updated successfully'


# TODO confirm if we remove delete & if so add the right permissions
class DeleteCenter(LoginRequiredMixin, DeleteView):
    """
    Remove a center
    """

    def post(self, request, *args, **kwargs):
        messages.success(request, 'center removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'core/centers/delete.html'
    model = models.AggregationCenter
    success_url = reverse_lazy('centers-list')


# TODO add the right permissions
# TODO add a breadcrump
class ProductList(LoginRequiredMixin, ListView):
    """
    A list of products
    """
    model = models.Product
    template_name = 'core/products/index.html'


# TODO add the right permissions
# TODO add a breadcrump
#  TODO remove create sub name and create name
@login_required()
def create_product(request):
    """
    Add a product
    :param request:
    :return return:
    """
    product_formset = modelformset_factory(models.Product, fields=('name', 'common_price'), extra=0, min_num=1)
    if request.method == 'POST':
        formset = product_formset(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Products added successfully!')
            return redirect(reverse_lazy('products-list'))
    else:
        formset = product_formset(queryset=models.Product.objects.none())
    return render(request, 'core/products/create.html', {'formset': formset,
                                                         'create_name': 'Products',
                                                         'create_sub_name': 'product'})


# TODO add the right permissions
# TODO add the breadcrump
class UpdateProduct(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update a certain product"""
    model = models.Product
    fields = ['name', 'common_price']
    template_name = 'crud/update.html'
    success_url = reverse_lazy('products-list')
    success_message = 'Product updated successfully'


# TODO confirm if delete & if then add the right permissions
class DeleteProduct(LoginRequiredMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'product removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'crud/delete.html'
    model = models.Product
    success_url = reverse_lazy('products-list')


# TODO add the right permissions
@login_required()
def product_availability_list(request, center):
    """
    A list of available products per center in a given day
    :param request:
    :param center:
    :return response:
    """
    center = get_object_or_404(models.AggregationCenter, pk=center)
    day = request.GET.get('day', None)
    if request.method == 'POST':
        day = request.POST['products_day']
        return redirect('add-product-availability', center=center.id, day=day)
    if day:
        day = datetime.strptime(day, "%Y-%m-%d").date()
    else:
        day = datetime.now().date()
    product_availability_list_items = models.AggregationCenterProduct.objects.filter(aggregation_center=center,
                                                                                     date=day)
    return render(request, 'core/centers/product-availabilty.html', {
        'products': product_availability_list_items,
        'center': center,
        'day': day
    })


# TODO add the right permissions
@login_required()
def product_availability(request, center, day):
    """
    used to indicate amount of products for sale in a center in a given day
    :param request:
    :param center:
    :param day:
    :return response:
    """
    dt = datetime.strptime(day, "%Y-%m-%d").date()
    center_product_formset = modelformset_factory(models.AggregationCenterProduct, fields=('product', 'qty'),
                                                  widgets={'product': Select2Widget}, extra=10, min_num=1,
                                                  can_delete=True)
    center = models.AggregationCenter.objects.get(pk=center)
    product_ids = [center_product.product.id for center_product in
                   center.aggregationcenterproduct_set.filter(date=dt)]
    products = models.Product.objects.exclude(pk__in=product_ids)
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
            return redirect(reverse('product-availability-list', kwargs={'center': center.id}))
    else:
        formset = center_product_formset(
            queryset=models.AggregationCenterProduct.objects.none())
        for form in formset:
            form.fields['product'].queryset = products
    return render(request, 'crud/formset-create.html', {'formset': formset,
                                                        "center": center,
                                                        'create_name': 'Products available in ' + center.name + ' on '
                                                                       + dt.strftime('%a %B %d, %Y'),
                                                        'create_sub_name': 'quantities'})


# TODO add the right permissions
@login_required()
def update_available_product(request, pk):
    """
    update available products
    :param request:
    :param pk:
    :return response:
    """
    product = get_object_or_404(models.AggregationCenterProduct, pk=pk)
    if request.method == 'POST':
        form = forms.AvailableProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'updated successfully')
            return redirect(reverse('product-availability-list', kwargs={'center': product.aggregation_center.id}))
    else:
        form = forms.AvailableProductForm(instance=product)
    return render(request, 'core/centers/update-product-availability.html', {
        'product': product, 'form': form
    })
