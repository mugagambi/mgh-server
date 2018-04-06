from django.urls import path
from sales import resource_views

urlpatterns = [
    path('customer/export/', resource_views.export_customers, name='export-customers')
]
