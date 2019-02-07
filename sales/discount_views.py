from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy

from sales.models import Customer, CustomerTotalDiscount, CustomerDiscount
from sales.forms import TotalDiscountForm, DiscountForm
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView

#TODO check permissions work
@login_required()
@permission_required('sales.view_discount')
def total_discounts(request, customer):
    customer = get_object_or_404(Customer, pk=customer)
    discount = CustomerTotalDiscount.objects.filter(customer=customer).first()
    return render(request, 'sales/customers/total_discounts.html',
                  {'discount': discount, 'customer': customer})

#TODO check permissions work
@login_required()
@permission_required('sales.change_customertotaldiscount')
def add_total_discounts(request, customer):
    customer = get_object_or_404(Customer, pk=customer)
    discount = CustomerTotalDiscount.objects.filter(customer=customer).exists()
    if discount:
        messages.error(request, 'A customer can\'t have  multiple total discounts')
        return redirect('customer_total_discounts', customer=customer.pk)
    if request.method == 'POST':
        form = TotalDiscountForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.customer = customer
            discount.save()
            messages.success(request, 'Customer discount added')
            return redirect('customer_total_discounts', customer=customer.pk)
    else:
        form = TotalDiscountForm()
    return render(request, 'sales/customers/add-discount.html', {'form': form,
                                                                 'customer': customer})


class UpdateDiscountView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required =  "sales.change_customertotaldiscount"
    model = CustomerTotalDiscount
    template_name = 'sales/customers/add-discount.html'
    fields = ['discount']
    success_message = 'Discount update successfully'

    def get_context_data(self, **kwargs):
        cxt = super(UpdateDiscountView, self).get_context_data(**kwargs)
        cxt['customer'] = get_object_or_404(Customer, pk=self.kwargs['customer'])
        return cxt

    def get_success_url(self):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer'])
        return reverse_lazy('customer_total_discounts', kwargs={'customer': customer.pk})


@login_required()
@permission_required('sales.view_discounts')
def customer_discounts(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    discounts = CustomerDiscount.objects.select_related('product').filter(customer=customer)
    return render(request, 'sales/customers/discounts.html', {'discounts': discounts, 'customer': customer})


class UpdateCustomerDiscountView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'sales.change_customerdiscount'
    model = CustomerDiscount
    template_name = 'sales/customers/update_discount.html'
    form_class = DiscountForm
    success_message = 'Discount update successfully'

    def get_context_data(self, **kwargs):
        cxt = super(UpdateCustomerDiscountView, self).get_context_data(**kwargs)
        cxt['customer'] = get_object_or_404(Customer, pk=self.kwargs['customer'])
        return cxt

    def get_success_url(self):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer'])
        return reverse_lazy('customer_discounts', kwargs={'pk': customer.pk})


class DeleteDiscount(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'sales.delete_customerdiscount'
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Discount removed successfully!')
        return super().post(request, *args, **kwargs)

    template_name = 'crud/delete.html'
    model = CustomerDiscount

    def get_success_url(self):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer'])
        return reverse_lazy('customer_discounts', kwargs={'pk': customer.pk})
