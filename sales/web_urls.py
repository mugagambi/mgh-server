from django.urls import path
from sales import web_views

urlpatterns = [
    path('orders/', web_views.OrdersView.as_view()),
    path('regions/', web_views.RegionList.as_view(), name='regions'),
    path('regions/create/', web_views.create_regions, name='create-region'),
    path('regions/<int:pk>/edit/', web_views.UpdateRegion.as_view(), name='update-region'),
    path('regions/<int:pk>/delete/', web_views.DeleteRegion.as_view(), name='delete-region'),
    path('customers/', web_views.CustomerList.as_view(), name='customers'),
    path('customers/create/', web_views.create_customer, name='create-customer'),
    path('customers/<pk>/delete/', web_views.DeleteCustomer.as_view(), name='delete-customer'),
    path('customers/<pk>/edit/', web_views.UpdateCustomer.as_view(), name='update-customer'),
    path('all/', web_views.SalesList.as_view(), name='total-sales'),
    path('customers/<pk>/prices/', web_views.add_prices, name='add-prices'),
    path('customers/<pk>/discounts/', web_views.add_discounts, name='add-discounts'),
    path('customers/<pk>/place-order/', web_views.place_order, name='place-order'),
]
