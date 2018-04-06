from django.db.models import Sum
from django.shortcuts import render

from core.models import Product
from sales import models
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required()
def sale_summary_report(request):
    cash = Product.objects.values('name', 'id').annotate(
        cash_qty=Sum('cashreceiptparticular__qty'),
        cash_total=Sum(
            'cashreceiptparticular__total')

    )
    customer = Product.objects.values('name', 'id').annotate(customer_qty=Sum('receiptparticular__qty'),
                                                             customer_total=Sum('receiptparticular__total', ))
    items = customer.union(cash).order_by('customer_total')
    return render(request, 'reports/sale_summary.html', {'items': items})
