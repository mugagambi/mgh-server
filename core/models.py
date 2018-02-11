from django.db import models
from django.contrib.auth.models import AbstractUser

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
        verbose_name_plural = 'Aggregation Center'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Items that the company sells
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AggregationCenterProduct(models.Model):
    """Products in a certain aggregation center"""
    aggregation_center = models.ForeignKey(AggregationCenter, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    active = models.BooleanField('Available', default=True, help_text='If the product is sale '
                                                                      'in this aggregation center')

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


class Grade(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name
