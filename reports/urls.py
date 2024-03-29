from django.urls import path

from reports import sales_summary, total_orders, product_sales, daily_sales_product, cash_deposit, market_returns, \
    customer_returns, cash_breakdown
from . import customer_orders
from . import customer_performance
from . import customer_sales
from . import daily_orders
from . import daily_orders_per_product
from . import daily_product_availability
from . import daily_sales
from . import order_dispatch
from . import outward_products
from . import outward_stock_summary
from . import price_per_product
from . import product_availabilty
from . import product_customer
from . import sales_per_region
from . import views

urlpatterns = [
    path('index/', views.index, name='report-index'),
    path('sales/', views.sale_summary_report, name='sales-summary'),
    path('sales/cash/<str:date_0>/<str:date_1>/', views.cash_sale_summary_report, name='cash-sales-summary'),
    path('sales/paybill/<str:date_0>/<str:date_1>/', views.mpesa_sale_summary_report, name='paybill-sales-summary'),
    path('sales/cheque/<str:date_0>/<str:date_1>/', views.cheque_sale_summary_report, name='cheque-sales-summary'),
    path('sales/bank/<str:date_0>/<str:date_1>/', views.bank_transfer_sale_summary_report, name='bank-sales-summary'),
    path('sales/outward_product/period/', outward_products.outward_product_summary_period,
         name='outward_product_period'),
    path('sales/outward_product/<str:date_0>/<str:date_1>/', outward_products.outward_product_summary_alt_report,
         name='outward_product_report'),
    path('sales/outward_stock/period/', outward_stock_summary.outward_stock_summary_period,
         name='outward_stock_period'),
    path('sales/outward-customer-product/period/', product_customer.outward_product_customer_summary_period,
         name='outward-product-per-customer-period'),
    path('sales/outward-customer-product/<str:date_0>/<str:date_1>/<int:product_id>/',
         product_customer.outward_product_summary_report_alt,
         name='outward-product-per-customer'),
    path('sales/outward_stock/<str:date_0>/<str:date_1>/', outward_stock_summary.outward_stock_summary_alt__report,
         name='outward_stock_report'),
    path('sales/sales_summary/period/', sales_summary.sales_summary_schedule,
         name='sales_summary_period'),
    path('sales/sales_summary/<str:date_0>/<str:date_1>/', sales_summary.sales_summary_report,
         name='sales_summary_report'),
    path('sales/price-per-product/period/', price_per_product.period, name='price_per_product_period'),
    path('sales/price-per-product/<str:date_0>/<str:date_1>/', price_per_product.report,
         name='price_per_product_report'),
    path('sales/price/<int:product_id>/<str:type>/<str:date_0>/<str:date_1>/', price_per_product.product_prices,
         name='product_group_prices'),
    path('sales/price/sales/<int:product_id>/<str:type>/<int:price>/<str:date_0>/<str:date_1>/',
         price_per_product.customer_sales_per_price,
         name='sales_per_price'),
    path('sales/customer-performance/period/', customer_performance.period, name='customer_performance_period'),
    path('sales/customer-perfomance/<str:customer>/<str:date_0>/<str:date_1>/', customer_performance.report,
         name='customer_performance_report'),
    path('sales/customer-perfomance/charts/<str:customer>/<str:date_0>/<str:date_1>/',
         customer_performance.get_json_response,
         name='customer_performance_chart'),
    path('sales/daily-sales/period/', daily_sales.period, name='daily_sales_period'),
    path('sales/daily-sales/<str:date_0>/<str:date_1>/', daily_sales.report,
         name='daily_sales_report'),
    path('sales/daily-sales/charts/<str:date_0>/<str:date_1>/', daily_sales.get_json_response,
         name='daily_sales_charts'),
    path('sales/customer-sales/period/', customer_sales.period, name='customer_sales_period'),
    path('sales/customer-sales/<str:customer>/<str:date_0>/<str:date_1>/', customer_sales.report,
         name='customer_sales_report'),
    path('sales/total-order/period/', total_orders.period, name='total_orders_period'),
    path('sales/total-order/<str:date_0>/<str:date_1>/', total_orders.report,
         name='total_orders_report'),
    path('sales/daily-order-per-product/period/', daily_orders.period, name='total_order_period'),
    path('sales/product-sales/period/', product_sales.period, name='product_sales_period'),
    path('sales/product-sales/<str:date_0>/<str:date_1>/', product_sales.report,
         name='product_sales_report'),
    path('sales/daily-sales-product/period/', daily_sales_product.period, name='daily_sales_product_period'),
    path('sales/daily-sales-product/<str:date_0>/<str:date_1>/<int:product>/', daily_sales_product.report,
         name='daily_sales_product_report'),
    path('sales/daily-cash-deposits/period/', cash_deposit.period, name='daily_cash_deposit_period'),
    path('sales/daily-cash-deposits/<str:date_0>/<str:date_1>/', cash_deposit.report,
         name='daily_cash_deposits_report'),
    path('sales/product-availability/period/', product_availabilty.period, name='product_availability_period'),
    path('sales/product-availability/<str:date_0>/<str:date_1>/', product_availabilty.report,
         name='product_availability_report'),
    path('sales/daily-product-availability/period/', daily_product_availability.period,
         name='daily_product_availability_period'),
    path('sales/daily-product-availability/<str:date_0>/<str:date_1>/<int:product>/', daily_product_availability.report,
         name='daily_product_availability_report'),
    path('sales/order-dispatch/period/', order_dispatch.period, name='order_dispatch_period'),
    path('sales/daily-product-availability/<str:date_0>/<str:date_1>/', order_dispatch.report,
         name='order_dispatch_report'),
    path('sales/daily-orders-product/period/', daily_orders_per_product.period, name='daily_orders_product_period'),
    path('sales/daily-orders-product/<str:date_0>/<str:date_1>/<int:product>/', daily_orders_per_product.report,
         name='daily_orders_product_report'),
    path('sales/customer-products/period/', customer_orders.period, name='customer_order_period'),
    path('sales/customer-products/<str:date_0>/<str:date_1>/<str:customer>/', customer_orders.report,
         name='customer_order_report'),
    path('sales/sales-per-region/period/', sales_per_region.period, name='sales_per_region_period'),
    path('sales/sales-per-region/<str:date_0>/<str:date_1>/', sales_per_region.report,
         name='sales_per_region_report'),
    path('sales/market-returns/period/', market_returns.period, name='market_returns_period'),
    path('sales/market-returns/<str:date_0>/<str:date_1>/', market_returns.report,
         name='market_returns_report'),
    path('sales/customer-returns/period/', customer_returns.period, name='customer_returns_period'),
    path('sales/customer-returns/<str:date_0>/<str:date_1>/', customer_returns.report,
         name='customer_returns_report'),
    path('sales/cash-breakdown/period/', cash_breakdown.period, name='cash_breakdown_period'),
    path('sales/cash-breakdown/<str:date_0>/<str:date_1>/', cash_breakdown.report,
         name='cash_breakdown_report'),
]
