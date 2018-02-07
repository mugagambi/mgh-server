from core import web_views
from django.urls import path

app_name = 'core'
urlpatterns = [
    path('users/groups', web_views.GroupListView.as_view(), name='groups'),
    path('users/groups/add', web_views.GroupCreateView.as_view(), name='group-create'),
    path('users/groups/<int:pk>/', web_views.GroupUpdateView.as_view(), name='group-edit')
]
