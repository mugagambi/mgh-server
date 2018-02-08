from core.view import groups
from django.urls import path

app_name = 'core'
urlpatterns = [
    path('users/groups', groups.GroupListView.as_view(), name='groups'),
    path('users/groups/add', groups.GroupCreateView.as_view(), name='group-create'),
    path('users/groups/<int:pk>/edit', groups.GroupUpdateView.as_view(), name='group-edit'),
    path('users/groups/<int:pk>/remove', groups.GroupDeleteView.as_view(), name='group-remove')
]
