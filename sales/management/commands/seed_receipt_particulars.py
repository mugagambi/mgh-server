import random

from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Product
from sales.models import Order, OrderProduct, Receipt,ReceiptParticular

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake receipt particulars'

    def handle(self, *args, **options):
        items = []
        products = Product.objects.all()
        for receipt in Receipt.objects.all():
            for i in range(0, 10):
                type = random.choice(['O', 'L'])
                qty = random.randint(10, 1000)
                product = random.choice(products)
                price = random.randint(50, 100)
                receipt = receipt
                total = price * qty
                items.append(ReceiptParticular(
                    type=type,
                    qty=qty,
                    product=product,
                    price=price,
                    receipt=receipt,
                    total=total
                ))
                msg = f'added receipt particular{type}, {qty}, {product}, {price}, {total}, {receipt}'
                print(msg)
        ReceiptParticular.objects.bulk_create(items)
