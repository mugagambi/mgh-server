from django.contrib.auth.mixins import PermissionRequiredMixin, AccessMixin, LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from sales.forms import ReturnForm
from sales.models import Return


class UpdateReturn(LoginRequiredMixin, PermissionRequiredMixin, AccessMixin, SuccessMessageMixin, UpdateView):
    model = Return
    permission_required = 'sales.delete_return'
    permission_denied_message = 'You don\'t have permission to update returns'
    raise_exception = True
    form_class = ReturnForm
    success_message = 'The return has been updated successfully'
    success_url = reverse_lazy('returns')
    template_name = 'sales/returns/create_returns.html'
