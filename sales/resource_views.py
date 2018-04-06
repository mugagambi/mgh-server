from datetime import datetime

from django.http import HttpResponse
from sales import resources


def export_customers(request):
    customer_resource = resources.CustomerResource()
    dataset = customer_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customer_%s.csv"' % str(datetime.now())
    return response
