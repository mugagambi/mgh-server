from django.db import models
from core.models import AggregationCenter


# Create your models here.

class Settings(models.Model):
    main_distribution = models.ForeignKey(AggregationCenter, on_delete=models.SET_NULL, null=True)
