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
router.register(r'customer-prices', views.CustomerPriceViewSet)
router.register(r'customer-discounts', views.CustomerDiscountsViewSet)
router.register(r'sales-crates', views.SalesCrateViewSet)
router.register(r'package-products-crates', views.PackageProductCrateViewSet)
router.register(r'receipts', views.ReceiptViewSet)
router.register(r'receipt-particulars', views.ReceiptParticularsViewSet)

urlpatterns = [
    path('', include(router.urls))
]
