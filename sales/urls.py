from django.urls import path, include
from rest_framework import routers
from sales import views

router = routers.DefaultRouter()
router.register(r'regions', views.RegionViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-products', views.OrderProductsViewSet)
router.register(r'packages', views.PackageViewSet)
router.register(r'package-products', views.PackageProductsViewSet)

urlpatterns = [
    path('', include(router.urls))
]
