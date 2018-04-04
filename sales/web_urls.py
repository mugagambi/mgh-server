from django.urls import path
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
    path('all/', web_views.SalesList.as_view(), name='total-sales'),
    path('all/receipt/<str:pk>', web_views.receipt_detail, name='sale-receipt'),
    path('all/cash', web_views.CashSalesList.as_view(), name='cash-sales'),
    path('customers/<str:pk>/prices/', web_views.add_prices, name='add-prices'),
    path('customers/<str:pk>/discounts/', web_views.add_discounts, name='add-discounts'),
    path('customers/<str:pk>/place-order/<str:date>/', web_views.place_order, name='place-order'),
    path('orders/', web_views.order_list, name='orders'),
    path('orders/distribute/', web_views.order_distribution_list, name='orders-distribute'),
    path('orders/<str:pk>/update/', web_views.update_order, name='update-order'),
    path('orders/<str:pk>/delete/', web_views.DeleteOrder.as_view(), name='delete-order'),
    path('orders/<str:pk>/', web_views.order_detail, name='order_detail'),
]
