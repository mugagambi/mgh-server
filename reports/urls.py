from django.urls import path
from . import views
from . import outward_products

urlpatterns = [
    path('index/', views.index, name='report-index'),
    path('sales/', views.sale_summary_report, name='sales-summary'),
    path('sales/cash/<str:date_0>/<str:date_1>/', views.cash_sale_summary_report, name='cash-sales-summary'),
    path('sales/outward_product/period/', outward_products.outward_product_summary_period,
         name='outward_product_period'),
    path('sales/outward_product/<str:date_0>/<str:date_1>/', outward_products.outward_product_summary_report,
         name='outward_product_report')
]
