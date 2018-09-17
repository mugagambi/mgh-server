from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminsList.as_view(), name='admin_list')
]