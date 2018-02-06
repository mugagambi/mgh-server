from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    phone_number = models.PositiveIntegerField(null=True)
    is_sales_agent = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class AggregationCenter(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AggregationCenterProduct(models.Model):
    aggregation_center = models.ForeignKey(AggregationCenter, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.aggregation_center)


class CrateType(models.Model):
    name = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class Crate(models.Model):
    number = models.CharField(max_length=10)
    type = models.ForeignKey(CrateType, on_delete=models.CASCADE)

    def __str__(self):
        return self.number


class Grade(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name
