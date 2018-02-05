from django.urls import path, include
from rest_framework import routers
from core import views

router = routers.DefaultRouter()
router.register(r'aggregation-centers', views.AggregationCenterViewSet)
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls))
]
