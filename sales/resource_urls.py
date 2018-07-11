from django.urls import path

from sales import resource_views

urlpatterns = [
    path('customer/export/', resource_views.export_customers, name='export-customers'),
    path('customer/statement/period/<str:customer>/', resource_views.export_customer_statement_period,
         name='customer_statement_period'),
    path('all/export/period/', resource_views.export_sales_period, name='export-sales-period'),
    path('cash-sales/export/period/', resource_views.export_cash_sales_period, name='cash_sale_period'),
    path('sales/export/<str:date_0>/<str:date_1>/', resource_views.export_customer_sales, name='export-customer-sales'),
    path('resources/cash_sale/<str:date_0>/<str:date_1>/', resource_views.GeneratePDF.as_view(), name='pdf-cash')
]
