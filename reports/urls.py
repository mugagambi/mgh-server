from django.urls import path

from reports import sales_summary
from . import views
from . import outward_products
from . import outward_stock_summary

urlpatterns = [
    path('index/', views.index, name='report-index'),
    path('sales/', views.sale_summary_report, name='sales-summary'),
    path('sales/cash/<str:date_0>/<str:date_1>/', views.cash_sale_summary_report, name='cash-sales-summary'),
    path('sales/paybill/<str:date_0>/<str:date_1>/', views.mpesa_sale_summary_report, name='paybill-sales-summary'),
    path('sales/cheque/<str:date_0>/<str:date_1>/', views.cheque_sale_summary_report, name='cheque-sales-summary'),
    path('sales/bank/<str:date_0>/<str:date_1>/', views.bank_transfer_sale_summary_report, name='bank-sales-summary'),
    path('sales/outward_product/period/', outward_products.outward_product_summary_period,
         name='outward_product_period'),
    path('sales/outward_product/<str:date_0>/<str:date_1>/', outward_products.outward_product_summary_report,
         name='outward_product_report'),
    path('sales/outward_stock/period/', outward_stock_summary.outward_stock_summary_period,
         name='outward_stock_period'),
    path('sales/outward_stock/<str:date_0>/<str:date_1>/', outward_stock_summary.outward_stock_summary_report,
         name='outward_stock_report'),
    path('sales/sales_summary/period/', sales_summary.sales_summary_schedule,
         name='sales_summary_period'),
    path('sales/sales_summary/<str:date_0>/<str:date_1>/', sales_summary.sales_summary_report,
         name='sales_summary_report'),
]
