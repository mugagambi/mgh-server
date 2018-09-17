from django.urls import path

from sales import discount_views
from sales import extra_views
from sales import generate_invoice_resource
from sales import market_returns_view
from sales import more_views
from sales import open_air
from sales import orderless_dispatch_view
from sales import receipts
from sales import returns_views
from sales import settle_debts_views
from sales import web_views

urlpatterns = [
    path('regions/', web_views.RegionList.as_view(), name='regions'),
    path('regions/create/', web_views.create_regions, name='create-region'),
    path('regions/<int:pk>/edit/', web_views.UpdateRegion.as_view(), name='update-region'),
    path('regions/<int:pk>/delete/', web_views.DeleteRegion.as_view(), name='delete-region'),
    path('customers/', web_views.customer_list, name='customers'),
    path('customers/create/', web_views.create_customer, name='create-customer'),
    path('customers/<str:pk>/delete/', web_views.DeleteCustomer.as_view(), name='delete-customer'),
    path('customers/<str:pk>/edit/', web_views.UpdateCustomer.as_view(), name='update-customer'),
    path('all/customers/', web_views.sales_list, name='total-sales'),
    path('all/invoices/', web_views.invoices_list, name='invoices'),
    path('all/bbfs/', web_views.bbf_accounts, name='bbfs'),
    path('all/debtors/', extra_views.trade_debtors, name='trade-debtors'),
    path('all/bbfs/<str:customer>/', web_views.customer_bbfs, name='customer-bbfs'),
    path('all/customers/receipt/<str:pk>/', web_views.receipt_detail, name='sale-receipt'),
    path('all/customers/receipt/<str:pk>/delete/', receipts.DeleteReceipt.as_view(), name='delete_sale_receipt'),
    path('all/receipt/create/', extra_views.add_receipt, name='create-sale-receipt'),
    path('all/cash/', web_views.cash_sales_list, name='cash-sales'),
    path('all/cash/add/<str:date>/', open_air.add_cash_receipt_particulars, name='add_cash_sales'),
    path('all/cash/<str:date>/', extra_views.cash_receipt, name='cash-receipt'),
    path('all/cash/particular<int:pk>/update/', open_air.update_open_air_sale, name='update_open_air_sale'),
    path('all/cash/particular<int:pk>/remove/', open_air.remove_open_air_sale, name='remove_open_air_sale'),
    path('all/debtors/<str:customer>/', extra_views.customer_statement, name='customer_statement'),
    path('all/debtors/<str:customer>/<str:date_0>/<str:date_1>/', extra_views.customer_statement,
         name='customer_statement_export'),
    path('customers/<str:pk>/prices/', web_views.customer_prices, name='customer_prices'),
    path('customers/<str:pk>/discounts/', discount_views.customer_discounts, name='customer_discounts'),
    path('customers/<str:customer>/discounts/<int:pk>/update/', discount_views.UpdateCustomerDiscountView.as_view(),
         name='update_customer_discounts'),
    path('customers/<str:customer>/discounts/<int:pk>/remove/', discount_views.DeleteDiscount.as_view(),
         name='delete_customer_discounts'),
    path('customers/<str:customer>/total/', discount_views.total_discounts, name='customer_total_discounts'),
    path('customers/<str:customer>/total/<int:pk>/update/', discount_views.UpdateDiscountView.as_view(),
         name='update_total_discount'),
    path('customers/<str:customer>/total/add/', discount_views.add_total_discounts, name='add_total_discounts'),
    path('customers/<str:customer>/deposits/', more_views.customer_deposits, name='customer_deposits'),
    path('customers/<str:customer>/deposits/add/', more_views.AddDeposit.as_view(), name='add_customer_deposit'),
    path('customers/<str:pk>/bbf/', web_views.add_bbf, name='add-customer-bff'),
    path('customers/<str:customer>/prices/<int:pk>/', web_views.update_price, name='update_customer_price'),
    path('customers/<str:pk>/discounts/add/', web_views.add_discounts, name='add-discounts'),
    path('customers/<str:pk>/place-order/<str:date_given>/', web_views.place_order, name='place-order'),
    path('orders/', web_views.order_list, name='orders'),
    path('orders/orderless/', more_views.orderless_dispatch, name='orderless_dispatch'),
    path('orders/orderless/update/',
         orderless_dispatch_view.update_orderless_dispatch,
         name='update_orderless'),
    path('orders/orderless/remove/', orderless_dispatch_view.remove_orderless_dispatch, name='remove_orderless'),
    path('orders/orderless/create/', orderless_dispatch_view.CreateOrderlessDispatch.as_view(),
         name='add_orderless'),
    path('order_distribute/', web_views.order_distribution_list, name='orders-distribute'),
    path('orders/distribute/<str:order_product>/', web_views.distribute_order, name='distribute-order'),
    path('orders/<str:order>/more/', web_views.add_more_products, name='more-items'),
    path('orders/<str:pk>/delete/', web_views.DeleteOrder.as_view(), name='delete-order'),
    path('orders/<str:pk>/', web_views.order_detail, name='order_detail'),
    path('orders/<str:order>/product/<str:pk>/', web_views.update_particular_item, name='update_order_product'),
    path('orders/<str:order>/remove-item', web_views.remove_order_product, name='remove_order_product'),
    path('all/returns/customers/', extra_views.ReturnsList.as_view(), name='returns'),
    path('all/returns/market/', more_views.market_returns, name='market_returns'),
    path('all/returns/market/create/', market_returns_view.CreateOrderlessDispatch.as_view(),
         name='create_market_return'),
    path('all/returns/market/update/', market_returns_view.update_market_return,
         name='update_market_return'),
    path('all/returns/market/remove/', market_returns_view.remove_market_return,
         name='remove_market_return'),
    path('all/returns/customers/<str:pk>/', extra_views.return_details, name='return'),
    path('all/returns/record/<str:customer>/', extra_views.record_return, name='record-return'),
    path('all/customers/receipt/<str:pk>/add-particular', extra_views.add_receipt_particular,
         name='add-sale-receipt'),
    path('all/customers/receipt/<str:receipt>/add-payment', extra_views.add_payment,
         name='add-sale-payment'),
    path('all/customers/receipt/<str:receipt>/update-payment/<int:payment>/', extra_views.update_payment,
         name='update-sale-payment'),
    path('all/customers/receipt/particular/<str:item>/update/', extra_views.update_particular,
         name='update-receipt-particular'),
    path('customers/settles/<str:deposit>/invoices/', settle_debts_views.settle_debt,
         name='settle_debt_invoices'),
    path('customers/settles/invoices/', settle_debts_views.settle_invoice_debt,
         name='settle_invoice'),
    path('invoice/generate/<str:customer>/<str:due_date>/', generate_invoice_resource.generate_invoice,
         name='generate_invoice'),
    path('all/returns/<str:pk>/update/', returns_views.UpdateReturn.as_view(), name='update_return')
]
