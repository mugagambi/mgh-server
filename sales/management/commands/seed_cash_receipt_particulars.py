import random

from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Product
from sales.models import CashReceiptParticular, CashReceipt

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake cash receipt particulars'

    def handle(self, *args, **options):
        items = []
        products = Product.objects.all()
        for receipt in CashReceipt.objects.all():
            for i in range(0, 10):
                qty = random.randint(10, 1000)
                product = random.choice(products)
                price = random.randint(50, 100)
                receipt = receipt
                total = price * qty
                items.append(CashReceiptParticular(
                    qty=qty,
                    product=product,
                    price=price,
                    cash_receipt=receipt,
                    total=total
                ))
                msg = f'added cash receipt particular {qty}, {product}, {price}, {total}, {receipt}'
                print(msg)
        CashReceiptParticular.objects.bulk_create(items)
