import random

from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Product
from sales.models import Customer, CustomerDiscount

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake orders'

    def handle(self, *args, **options):
        items = []
        customers = Customer.objects.all()
        products = Product.objects.all()
        for i in range(0, 1000):
            customer = random.choice(customers)
            discount = random.randint(0, 10)
            product = random.choice(products)
            items.append(CustomerDiscount(
                customer=customer,
                discount=discount,
                product=product
            ))
            msg = f'added discount {customer}, {discount}, {product}'
            print(msg)
        CustomerDiscount.objects.bulk_create(items)
