from decimal import Decimal
from functools import reduce

from django.db import models
from django.utils.timezone import now

from core.models import User, Product, Crate, AggregationCenter


# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Customer(models.Model):
    email = models.EmailField(null=True, blank=True)
    number = models.CharField(max_length=10, unique=True, primary_key=True)
    shop_name = models.CharField(max_length=100, unique=True)
    nick_name = models.CharField(blank=True, max_length=100)
    location = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, help_text='search by region name')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Shop name ' + str(self.shop_name) + ' , nick_name ' + str(self.nick_name)


class Order(models.Model):
    customer = models.ForeignKey(Customer, to_field='number', on_delete=models.CASCADE,
                                 help_text='search by customer no. , shop name or nick name')
    number = models.CharField(max_length=10, unique=True, primary_key=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_delivery = models.DateField('date of delivery')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date_delivery', '-created_at')

    def __str__(self):
        return 'order no. ' + str(self.number) + ' for ' + str(self.customer.shop_name)

    def total_qty(self):
        if self.orderproduct_set.all().exists():
            return reduce((lambda x, y: x + y), [x.qty for x in self.orderproduct_set.all()])
        return 0

    def total_price(self):
        if self.orderproduct_set.all().exists():
            return reduce((lambda x, y: x + y), [x.price.price for x in self.orderproduct_set.all()])
        return 0


class CustomerPrice(models.Model):
    customer = models.ForeignKey(Customer, to_field='number',
                                 help_text='search by customer no. , shop name or nick name',
                                 on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, help_text='This is the unit'
                                                                          ' price for each quantity')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='search by product name')
    negotiated_price = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.product) + ' for ksh. ' + str(self.price)

    class Meta:
        unique_together = ('customer', 'product')


class CustomerDiscount(models.Model):
    customer = models.ForeignKey(Customer, to_field='number', on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=5, decimal_places=2,
                                   help_text='% discount')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='search by product name')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'product')

    def __str__(self):
        return str(self.product) + ' for ' + str(self.discount) + '%'


class OrderProduct(models.Model):
    number = models.CharField(max_length=10, unique=True, primary_key=True)
    order = models.ForeignKey(Order, to_field='number', on_delete=models.CASCADE, help_text='search by order no.')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    price = models.ForeignKey(CustomerPrice, on_delete=models.SET_NULL, null=True)
    discount = models.ForeignKey(CustomerDiscount, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return 'item for order ' + str(self.order) + '-> ' + str(self.product.name)

    class Meta:
        verbose_name = 'Order Report'
        verbose_name_plural = 'Order Reports'


class OrderDistributionPoint(models.Model):
    center = models.ForeignKey(AggregationCenter, on_delete=models.SET_NULL, null=True)
    order_product = models.ForeignKey(OrderProduct, on_delete=models.SET_NULL, null=True)
    qty = models.DecimalField(decimal_places=2, max_digits=8)

    def __str__(self):
        return str(self.center)


class Package(models.Model):
    order = models.ForeignKey(Order, to_field='number', on_delete=models.CASCADE)
    number = models.CharField(max_length=10, unique=True, primary_key=True)
    packaged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'package no. ' + str(self.number)


class PackageProduct(models.Model):
    number = models.CharField(max_length=10, unique=True, primary_key=True)
    package = models.ForeignKey(Package, to_field='number', on_delete=models.CASCADE)
    order_product = models.ForeignKey(OrderProduct, to_field='number', on_delete=models.CASCADE)
    qty_weigh = models.DecimalField(decimal_places=2, max_digits=8)
    crate_weight = models.DecimalField(decimal_places=2, max_digits=4)

    def __str__(self):
        return 'items for ' + str(self.package)

    class Meta:
        verbose_name_plural = 'Packed Products'


class SalesCrate(models.Model):
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    crate = models.ForeignKey(Crate, to_field='number', on_delete=models.CASCADE, help_text='search by crate number')
    date_issued = models.DateField()
    date_returned = models.DateField(null=True)
    held_by = models.ForeignKey(Customer, to_field='number', on_delete=models.SET_NULL, null=True,
                                help_text='search by customer no. , shop name or nick name')

    def __str__(self):
        return 'crate no. ' + str(self.crate.number) + ' for  agent ' + str(self.agent)


class PackageProductCrate(models.Model):
    crate = models.ForeignKey(Crate, to_field='number', on_delete=models.CASCADE, help_text='search by crate number')
    package_product = models.ForeignKey(PackageProduct, to_field='number', on_delete=models.CASCADE,
                                        help_text='search package item')

    def __str__(self):
        return str(self.crate)


class Receipt(models.Model):
    number = models.CharField(unique=True, max_length=10, primary_key=True)
    customer = models.ForeignKey(Customer, to_field='number', on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    served_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    bbf_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return 'Receipt no ' + ' ' + str(self.number)

    class Meta:
        verbose_name_plural = 'Sales'
        verbose_name = 'Sale'

    def has_credit(self):
        return self.receiptpayment_set.filter(type=4).exists()


class ReceiptParticular(models.Model):
    TYPE = (
        ('O', 'Ordered'),
        ('L', 'Orderless')
    )
    type = models.CharField(max_length=1, choices=TYPE, default='O')
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, help_text='This is the unit'
                                                                          'price for each quantity')
    discount = models.DecimalField(max_digits=5, decimal_places=2,
                                   help_text='% discount', null=True)
    receipt = models.ForeignKey(Receipt, to_field='number', on_delete=models.CASCADE)
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
    receipt = models.ForeignKey(Receipt, to_field='number', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.PositiveSmallIntegerField(choices=TYPES)
    check_number = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=15, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    date_to_pay = models.DateField(null=True)
    transfer_code = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.receipt)


class CashReceipt(models.Model):
    number = models.CharField(unique=True, max_length=10, primary_key=True)
    date = models.DateTimeField(default=now)
    served_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return 'cash receipt no. ' + str(self.date)


class CashReceiptParticular(models.Model):
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, help_text='This is the unit'
                                                                          'price for each quantity')
    cash_receipt = models.ForeignKey(CashReceipt, to_field='number', on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.cash_receipt)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        amount = self.qty * self.price
        self.total = amount
        return super(CashReceiptParticular, self).save(force_insert=False, force_update=False, using=None,
                                                       update_fields=None)


class CashReceiptPayment(models.Model):
    TYPES = (
        (1, 'Mpesa'),
        (2, 'Cash')
    )
    cash_receipt = models.ForeignKey(CashReceipt, to_field='number', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.PositiveSmallIntegerField(choices=TYPES)
    check_number = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=15, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    date_to_pay = models.DateField(null=True)
    transfer_code = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.cash_receipt)


class CreditSettlement(models.Model):
    TYPES = (
        (1, 'Cheque'),
        (2, 'Mpesa'),
        (3, 'Cash'),
        (4, 'Bank Transfer')
    )
    number = models.CharField(unique=True, max_length=10, primary_key=True)
    type = models.PositiveSmallIntegerField(choices=TYPES)
    customer = models.ForeignKey(Customer, to_field='number', on_delete=models.CASCADE, help_text='search by customer')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    check_number = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=15, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    transfer_code = models.CharField(max_length=50, blank=True)
    date = models.DateTimeField(default=now)
    recorded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'credit settlement no. ' + str(self.number)


class BBF(models.Model):
    BFF_TYPE = (
        ('p', 'Balance Carried Forward'),
        ('r', 'Returns Credit Note'),
        ('c', 'Credit Settlement Excess'),
        ('s', 'Pre System')
    )
    receipt = models.ForeignKey(Receipt, to_field='number', on_delete=models.SET_NULL,
                                help_text='search by receipt no.', null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                 help_text='(-) are amounts the customer owes Meru Greens'
                                           ' and (+) are amounts that Meru Greens owes the'
                                           'customer')
    bbf_type = models.CharField(max_length=1, choices=BFF_TYPE)
    customer = models.ForeignKey(Customer, to_field='number', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return 'balance ' + str(self.receipt)


class BbfBalance(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.customer)

    class Meta:
        ordering = ('balance',)


class Return(models.Model):
    number = models.CharField(unique=True, max_length=10, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='search product name')
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    receipt = models.ForeignKey(Receipt, to_field='number', on_delete=models.CASCADE, help_text='search receipt no')
    customer = models.ForeignKey(Customer, to_field='number', on_delete=models.CASCADE,
                                 help_text='search by customer number, shop name and nick name')
    description = models.TextField()
    date = models.DateTimeField(default=now)

    def __str__(self):
        return 'return number ' + str(self.number)


class Reject(models.Model):
    number = models.CharField(unique=True, max_length=10, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='search by product name')
    qty = models.DecimalField(decimal_places=2, max_digits=8)
    receipt = models.ForeignKey(Receipt, to_field='number', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, to_field='number', on_delete=models.CASCADE,
                                 help_text='search by customer number, shop name and nick name')
    description = models.TextField()
    date = models.DateTimeField(default=now)
    refund_qty = models.DecimalField(decimal_places=2, max_digits=8, null=True)
    refund_date = models.DateTimeField(null=True)

    def __str__(self):
        return 'reject number ' + str(self.number)


class Invoices(Receipt):
    class Meta:
        proxy = True
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
