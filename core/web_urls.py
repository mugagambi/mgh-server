from core import web_views
from django.urls import path

app_name = 'core'
urlpatterns = [
    path('users/groups', web_views.GroupListView.as_view(), name='groups')
]
