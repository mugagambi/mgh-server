from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404

from sales import models
import django_filters


class OrderlessFilter(django_filters.FilterSet):
    class Meta:
        model = models.OrderlessPackage
        fields = ('product',)


# todo add the right permissions
# todo order by date in decreasing order and probably group by dates and give details
@login_required()
def orderless_dispatch(request):
    """
    show all orderless dispatch starting with the latest and add a filter bar
    :param request:
    :return:
    """
    orderless_list = models.OrderlessPackage.objects.select_related('product').all()
    orderless_filter = OrderlessFilter(request.GET, queryset=orderless_list)
    orderless_list = orderless_filter.qs
    paginator = Paginator(orderless_list, 50)
    page = request.GET.get('page', 1)
    try:
        orderless = paginator.page(page)
    except PageNotAnInteger:
        orderless = paginator.page(1)
    except EmptyPage:
        orderless = paginator.page(paginator.num_pages)
    args = {'paginator': paginator, 'filter': orderless_filter,
            'orderless': orderless}
    return render(request, 'sales/orderless/index.html', args)


@login_required()
def customer_deposits(request, customer):
    customer = get_object_or_404(models.Customer, pk=customer)
    deposits = models.CustomerDeposit.objects.filter(customer=customer)
    paginator = Paginator(deposits, 50)
    page = request.GET.get('page', 1)
    try:
        deposits = paginator.page(page)
    except PageNotAnInteger:
        deposits = paginator.page(1)
    except EmptyPage:
        deposits = paginator.page(paginator.num_pages)
    return render(request, 'sales/customers/deposits.html', {'paginator': paginator, 'deposits': deposits,
                                                             'customer': customer})
