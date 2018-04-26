from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from django.utils.timezone import now


class User(AbstractUser):
    phone_number = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.username


class AggregationCenter(models.Model):
    """
    The place where products are incubated, processed and packaged to be
    delivered to the customers
    """
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Aggregation Center'
        verbose_name_plural = 'Aggregation Centers'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Items that the company sells
    """
    name = models.CharField(max_length=100, unique=True)
    common_price = models.DecimalField(max_digits=9, decimal_places=2, default=0.0, help_text='price in Ksh.')

    def __str__(self):
        return self.name


class AggregationCenterProduct(models.Model):
    """Products in a certain aggregation center"""
    aggregation_center = models.ForeignKey(AggregationCenter, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.DecimalField(decimal_places=2, max_digits=8, help_text='in kgs.')
    date = models.DateField(default=now)
    remaining = models.DecimalField(decimal_places=2, max_digits=8, help_text='in kgs.', default=0)

    def __str__(self):
        return str(self.product) + ' at ' + str(self.aggregation_center)


class CrateType(models.Model):
    name = models.CharField(max_length=100)
    weight = models.DecimalField('Weight (kgs)', max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class Crate(models.Model):
    number = models.CharField(max_length=10, unique=True)
    type = models.ForeignKey(CrateType, on_delete=models.CASCADE)
    procurement_date = models.DateField(default=now)

    def __str__(self):
        return self.number
