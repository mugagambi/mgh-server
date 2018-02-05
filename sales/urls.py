from django.urls import path, include
from rest_framework import routers
from sales import views

router = routers.DefaultRouter()
router.register(r'regions', views.RegionViewSet)

urlpatterns = [
    path('', include(router.urls))
]
