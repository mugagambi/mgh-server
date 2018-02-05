from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    phone_number = models.PositiveIntegerField()
    is_sales_agent = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Product(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Crate(models.Model):
    TYPE = (
        (1, 'normal crate'),
    )
    number = models.CharField(max_length=10)
    type = models.PositiveSmallIntegerField(choices=TYPE)

    def __str__(self):
        return self.number


class Grade(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name
