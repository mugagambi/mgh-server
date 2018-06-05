from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from system_settings import views

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
    path('change-password/', views.change_password, name='change_password'),
    path('users/<str:username>/permission', views.assign_permissions, name='assign-permission'),
    path('settings/billings/', views.BilledTogetherView.as_view(), name='billings'),
    path('settings/billings/add/', views.AddBilling.as_view(), name='add_billing'),
    path('settings/billings/<int:pk>/update/', views.UpdateBillingView.as_view(), name='update_billing'),
    path('settings/billings/<int:pk>/delete/', views.DeleteBilling.as_view(), name='delete_billing'),
    path('settings/billings/<int:billing>/customers/', views.billing_group_customer_list, name='customer_list'),
    path('settings/billings/<int:billing>/customers/<int:pk>/remove/', views.RemoveCustomer.as_view(),
         name='remove_customer')
]
