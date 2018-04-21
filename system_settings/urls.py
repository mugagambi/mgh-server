from django.urls import path
from system_settings import views

urlpatterns = [
    path('settings/main-center/', views.main_center_setting, name='main-center'),
    path('users/', views.SystemUsersList.as_view(), name='users'),
    path('users/create', views.create_user, name='create-user'),
    path('users/deactivate', views.deactivate_user, name='deactivate-users'),
]
