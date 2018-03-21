from django.urls import path
from django.contrib.auth.views import LoginView, logout_then_login
from core import web_views

urlpatterns = [
    path('sign-in/', LoginView.as_view(template_name='core/sign-in.html'), name='sign-in'),
    path('logout/', logout_then_login, name='log-out'),
    path('centers/', web_views.CentersList.as_view(), name='centers-list'),
    path('centers/create', web_views.create_centers, name='create-center'),
    path('centers/<int:pk>/edit/', web_views.UpdateCenter.as_view(), name='update-center'),
    path('centers/<int:pk>/delete/', web_views.DeleteCenter.as_view(), name='delete-center'),
]
