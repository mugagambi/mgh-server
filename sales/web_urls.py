from django.urls import path
from sales import web_views
from sales import extra_views
from sales import resource_views

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
    path('all/receipt/create/', extra_views.add_receipt, name='create-sale-receipt'),
    path('all/cash/', web_views.cash_sales_list, name='cash-sales'),
    path('all/cash/<str:day>/', extra_views.cash_receipt, name='cash-receipt'),
    path('all/debtors/<str:customer>/', extra_views.customer_statement, name='customer_statement'),
    path('customers/<str:pk>/prices/', web_views.customer_prices, name='customer_prices'),
    path('customers/<str:pk>/bbf/', web_views.add_bbf, name='add-customer-bff'),
    path('customers/<str:customer>/prices/<int:pk>/', web_views.update_price, name='update_customer_price'),
    path('customers/<str:pk>/discounts/', web_views.add_discounts, name='add-discounts'),
    path('customers/<str:pk>/place-order/<str:date_given>/', web_views.place_order, name='place-order'),
    path('orders/', web_views.order_list, name='orders'),
    path('orders/distribute/', web_views.order_distribution_list, name='orders-distribute'),
    path('orders/distribute/<str:order_product>/', web_views.distribute_order, name='distribute-order'),
    path('orders/<str:order>/more/', web_views.add_more_products, name='more-items'),
    path('orders/<str:pk>/delete/', web_views.DeleteOrder.as_view(), name='delete-order'),
    path('orders/<str:pk>/', web_views.order_detail, name='order_detail'),
    path('orders/<str:order>/product/<str:pk>/', web_views.update_particular_item, name='update_order_product'),
    path('orders/<str:order>/remove-item', web_views.remove_order_product, name='remove_order_product'),
    path('all/returns', extra_views.ReturnsList.as_view(), name='returns'),
    path('all/returns/record/<str:customer>/', extra_views.record_return, name='record-return'),
    path('all/customers/receipt/<str:pk>/add-particular', extra_views.add_receipt_particular,
         name='add-sale-receipt'),
    path('resources/cash_sale/<str:day>/', resource_views.GeneratePDF.as_view(), name='pdf-cash')
]
