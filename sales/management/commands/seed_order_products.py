import random

from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Product
from sales.models import Order, OrderProduct
from utils import generate_unique_id

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake order products'

    def handle(self, *args, **options):
        items = []
        orders = Order.objects.all()
        products = Product.objects.all()
        for i in range(0, 100000):
            number = generate_unique_id(i)
            order = random.choice(orders)
            product = random.choice(products)
            qty = random.randint(10, 1000)
            items.append(OrderProduct(
                number=number,
                order=order,
                product=product,
                qty=qty
            ))
        OrderProduct.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS('seeded order products'))
