from django.urls import path

from . import views

urlpatterns = [
    path('banks/', views.BankList.as_view(), name='banks'),
    path('banks/create/', views.create_banks, name='create_banks'),
    path('banks/<int:pk>/update/', views.UpdateBank.as_view(), name='update_bank'),
    path('banks/<int:pk>/delete/', views.DeleteBank.as_view(), name='delete_bank'),
    path('cash-deposits/', views.CashDepositList.as_view(), name='cash_deposits'),
    path('cash-deposits/create/', views.add_deposits, name='add_deposits'),
    path('cash-deposits/<int:pk>/update/', views.UpdateCashDeposit.as_view(), name='update_deposit'),
]
