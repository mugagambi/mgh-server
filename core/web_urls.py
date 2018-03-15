from django.urls import path
from django.contrib.auth.views import LoginView, logout_then_login

urlpatterns = [
    path('sign-in/', LoginView.as_view(template_name='core/sign-in.html'), name='sign-in'),
    path('logout/', logout_then_login, name='log-out')
]
