from django.urls import path, re_path
from system_settings import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('settings/main-center/', views.main_center_setting, name='main-center'),
    path('users/', views.SystemUsersList.as_view(), name='users'),
    path('users/create', views.create_user, name='create-user'),
    path('users/deactivate', views.deactivate_user, name='deactivate-users'),
    path('password_reset/', auth_views.password_reset, name='main-password_reset'),
    path('password_reset/done/', auth_views.password_reset_done, name='main-password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.password_reset_confirm, name='main-password_reset_confirm'),
    path('reset/done/', auth_views.password_reset_complete, name='main-password_reset_complete'),
    path('change-password/', views.change_password, name='change_password')
]
