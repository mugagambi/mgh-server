from django.urls import path
from sales import web_views

urlpatterns = [
    path('orders/', web_views.OrdersView.as_view()),
    path('regions/', web_views.RegionList.as_view(), name='regions')
]
