from decimal import Decimal
from django.db import models
from core.models import User, Product, Crate, AggregationCenter
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from functools import reduce


# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(name='shop_name', max_length=100)
    nick_name = models.CharField(blank=True, max_length=100)
    location = models.CharField(max_length=100)
    country_code = models.PositiveSmallIntegerField()
    phone_number = models.PositiveIntegerField(unique=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.shop_name)


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_delivery = models.DateField('date of delivery', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.customer)


class OrderProducts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return str(self.order)

    class Meta:
        verbose_name = 'Order Report'
        verbose_name_plural = 'Order Reports'


class Package(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    packaged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order)


class PackageProduct(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty_order = models.DecimalField(decimal_places=2, max_digits=8)
    qty_weigh = models.DecimalField(decimal_places=2, max_digits=8)
    crate_weight = models.DecimalField(decimal_places=2, max_digits=4)

    def __str__(self):
        return str(self.package)

    class Meta:
        verbose_name_plural = 'Packed Products'


class CustomerPrice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, help_text='This is the unit'
                                                                          'price for each quantity')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.customer)


class CustomerDiscount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=5, decimal_places=2,
                                   help_text='% discount')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
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


class PackageProductCrate(models.Model):
    crate = models.ForeignKey(Crate, on_delete=models.CASCADE)
    package_product = models.ForeignKey(PackageProduct, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.crate)


class Receipt(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    served_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.customer)

    class Meta:
        verbose_name_plural = 'Sales'
        verbose_name = 'Sale'

    def total_qty(self):
        if self.receiptparticular_set.all().exists():
            return reduce((lambda x, y: x + y), [x.qty for x in self.receiptparticular_set.all()])
        return 0

    def total_amount(self):
        if self.receiptparticular_set.all().exists():
            return reduce((lambda x, y: x + y), [x.total for x in self.receiptparticular_set.all()])
        return 0

    def total_payment(self):
        if self.receiptpayment_set.all().exists():
            return reduce((lambda x, y: x + y), [x.amount for x in self.receiptpayment_set.all()])
        return 0

    def balance(self):
        return self.total_payment() - self.total_amount()


class ReceiptParticular(models.Model):
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, help_text='This is the unit'
                                                                          'price for each quantity')
    discount = models.DecimalField(max_digits=5, decimal_places=2,
                                   help_text='% discount', null=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.receipt)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        amount = self.qty * self.price
        if self.discount:
            total_discount = Decimal(amount) * (Decimal(self.discount) / 100)
            self.total = amount - total_discount
            return super(ReceiptParticular, self).save(force_insert=False, force_update=False, using=None,
                                                       update_fields=None)
        self.total = amount
        print(self.total)
        return super(ReceiptParticular, self).save(force_insert=False, force_update=False, using=None,
                                                   update_fields=None)


class ReceiptPayment(models.Model):
    TYPES = (
        (1, 'Cheque'),
        (2, 'Mpesa'),
        (3, 'Cash'),
        (4, 'Credit'),
        (5, 'Bank Transfer')
    )
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.PositiveSmallIntegerField(choices=TYPES)
    check_number = models.CharField(max_length=50, null=True)
    transaction_id = models.CharField(max_length=15, null=True)
    mobile_number = models.CharField(max_length=15, null=True)
    date_to_pay = models.DateField(null=True)
    transfer_code = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.receipt)


class CashReceipt(models.Model):
    date = models.DateTimeField(default=now)
    served_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.date)


class CashReceiptParticular(models.Model):
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, help_text='This is the unit'
                                                                          'price for each quantity')
    discount = models.DecimalField(max_digits=5, decimal_places=2,
                                   help_text='% discount')
    cash_receipt = models.ForeignKey(CashReceipt, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.cash_receipt)


class CashReceiptPayment(models.Model):
    TYPES = (
        (1, 'Cheque'),
        (2, 'Mpesa'),
        (3, 'Cash'),
        (4, 'Credit'),
        (5, 'Bank Transfer')
    )
    cash_receipt = models.ForeignKey(CashReceipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.PositiveSmallIntegerField(choices=TYPES)
    check_number = models.CharField(max_length=50, null=True)
    transaction_id = models.CharField(max_length=15, null=True)
    mobile_number = models.CharField(max_length=15, null=True)
    date_to_pay = models.DateField(null=True)
    transfer_code = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.cash_receipt)


class CreditSettlement(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=now)
    served_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.receipt)


class OverPayOrUnderPay(models.Model):
    TYPE = (
        ('o', 'OverPay'),
        ('u', 'Underpay')
    )
    type = models.CharField(max_length=1, choices=TYPE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.customer)


class ReturnsOrRejects(models.Model):
    TYPE = (
        (1, 'Return'),
        (2, 'Reject')
    )
    type = models.PositiveSmallIntegerField(choices=TYPE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.TextField()
    date = models.DateTimeField(default=now)
    date_of_resuplly = models.DateField(null=True)
