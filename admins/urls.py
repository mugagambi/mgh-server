from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminsList.as_view(), name='admin_list'),
    path('add/', views.CreateAdmin.as_view(), name='add_admin')
]