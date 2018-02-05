from django.urls import path, include
from rest_framework import routers
from sales import views

router = routers.DefaultRouter()
router.register(r'regions', views.RegionViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-products', views.OrderProductsViewSet)

urlpatterns = [
    path('', include(router.urls))
]
