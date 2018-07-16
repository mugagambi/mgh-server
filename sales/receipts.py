from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from sales import models


class DeleteReceipt(LoginRequiredMixin, PermissionRequiredMixin, AccessMixin, DeleteView):
    permission_required = 'sales.delete_receipt'
    raise_exception = True
    permission_denied_message = 'You don\'t have permission to perform this action'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        payments = self.object.receiptpayment_set.exclude(type=4).aggregate(total=Sum('amount'))
        total_purchases = self.object.receiptparticular_set.aggregate(total=Sum('total'))
        account_balance = models.CustomerAccountBalance.objects.get(customer=self.object.customer)
        account_balance.amount = account_balance.amount + total_purchases['total'] if total_purchases['total'] else 0
        account_balance.save()
        account_balance.amount = account_balance.amount - payments['total'] if payments['total'] else 0
        account_balance.save()
        models.CustomerAccount.objects.filter(receipt=self.object).delete()
        messages.success(request, 'Receipt removed successfully.Customer accounts statement have been adjusted')
        return super(DeleteReceipt, self).delete(request, *args, **kwargs)

    template_name = 'core/centers/delete.html'
    model = models.Receipt
    success_url = reverse_lazy('total-sales')
