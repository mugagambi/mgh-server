from django.urls import path
from system_settings import views

urlpatterns = [
    path('main-center/', views.main_center_setting, name='main-center'),
    path('system-users/', views.SystemUsersList.as_view(), name='users'),
    path('system-users/create', views.create_user, name='create-user'),
    path('system-users/deactivate', views.deactivate_user, name='deactivate-users'),
]
