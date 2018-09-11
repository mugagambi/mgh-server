import random

from django.core.management.base import BaseCommand
from faker import Faker

from core.models import Product

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 200 fake products with common prices ranging from 50 to 150'

    def handle(self, *args, **options):
        items = []
        for i in range(0, 50):
            name = 'product' + ' ' + str(i)
            common_price = random.randint(50, 100)
            items.append(Product(
                name=name,
                common_price=common_price
            ))
            msg = f'added product {name}, {common_price}'
            print(msg)
        Product.objects.bulk_create(items)
