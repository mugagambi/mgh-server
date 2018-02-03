from django.db import models
from core.models import User, Product, Crate
from django.core.exceptions import ValidationError


# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    country_code = models.PositiveSmallIntegerField()
    phone_number = models.PositiveIntegerField()
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_delivery = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.customer)


class OrderProducts(models.Model):
    GRADES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4)
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    grade = models.PositiveSmallIntegerField(choices=GRADES)
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return str(self.order)


class Package(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    packaged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order)


class PackageProduct(models.Model):
    GRADES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4)
    )
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty_order = models.DecimalField(decimal_places=2, max_digits=8)
    qty_weigh = models.DecimalField(decimal_places=2, max_digits=8)
    crate_weight = models.DecimalField(decimal_places=2, max_digits=4)
    grade = models.PositiveSmallIntegerField(choices=GRADES)

    def __str__(self):
        return str(self.package)


class CustomerPrice(models.Model):
    GRADES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4)
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, help_text='This is the unit'
                                                                          'price for each quantity')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    grade = models.PositiveSmallIntegerField(choices=GRADES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.customer)


class CustomerDiscount(models.Model):
    GRADES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4)
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=5, decimal_places=2,
                                   help_text='% discount')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    grade = models.PositiveSmallIntegerField(choices=GRADES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.customer)


class SalesCrate(models.Model):
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    crate = models.ForeignKey(Crate, on_delete=models.CASCADE)
    date_issued = models.DateField()
    date_returned = models.DateField(null=True)
    held_by = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.agent)

    def clean_fields(self, exclude=None):
        if not self.agent.is_sales_agent:
            raise ValidationError({'agent': ['agent must be a sales agent']})


class PackageProductCrate(models.Model):
    crate = models.ForeignKey(Crate, on_delete=models.CASCADE)
    package_product = models.ForeignKey(PackageProduct, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.crate)
