from django.views.generic import TemplateView


class OrdersView(TemplateView):
    template_name = 'sales/orders.html'
