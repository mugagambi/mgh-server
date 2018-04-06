from django.urls import path
from . import views

urlpatterns = [
    path('sales/', views.sale_summary_report, name='sales-summary')
]
