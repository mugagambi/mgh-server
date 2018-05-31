from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy

from sales.models import Customer, CustomerTotalDiscount
from sales.forms import TotalDiscountForm
from django.contrib import messages
from django.views.generic import UpdateView


@login_required()
def total_discounts(request, customer):
    customer = get_object_or_404(Customer, pk=customer)
    discount = CustomerTotalDiscount.objects.filter(customer=customer).first()
    return render(request, 'sales/customers/total_discounts.html',
                  {'discount': discount, 'customer': customer})


@login_required()
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


class UpdateDiscountView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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
