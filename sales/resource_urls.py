from django.urls import path
from sales import resource_views

urlpatterns = [
    path('customer/export/', resource_views.export_customers, name='export-customers'),
    path('sales/export/period/', resource_views.export_sales_period, name='export-sales-period'),
    path('sales/export/<str:date_0>/<str:date_1>/', resource_views.export_customer_sales, name='export-customer-sales')
]
