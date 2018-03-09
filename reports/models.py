from django.db import models
from sales.models import ReceiptParticular, Receipt


# Create your models here.
class SaleSummary(ReceiptParticular):
    class Meta:
        proxy = True
        verbose_name = 'Outwards Stocks Summary'
        verbose_name_plural = 'Outwards Stocks Summary'
