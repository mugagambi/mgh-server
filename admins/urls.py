from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminsList.as_view(), name='admin_list'),
    path('add/', views.CreateAdmin.as_view(), name='add_admin'),
    path('add/<int:pk>/update/', views.UpdateAdmin.as_view(), name='change_admin'),
    path('add/<int:pk>/delete/', views.remove_admin, name='remove_admin')
]