from django.urls import path, include
from rest_framework import routers
from core.view import api

router = routers.DefaultRouter()
router.register(r'aggregation-centers', api.AggregationCenterViewSet)
router.register(r'products', api.ProductViewSet)
router.register(r'aggregation-centers-products', api.AggregationCenterProductViewSet)
router.register(r'crate-types', api.CrateTypeViewSet)
router.register(r'crates', api.CrateViewSet)
router.register(r'grades', api.GradeViewSet)

urlpatterns = [
    path('', include(router.urls))
]
