from django.urls import path
from system_settings import views

urlpatterns = [
    path('main-center/', views.main_center_setting, name='main-center')
]
