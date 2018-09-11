import random

from django.core.management.base import BaseCommand
from faker import Faker

from sales.models import OrderProduct, Package, PackageProduct
from utils import generate_unique_id

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake package products'

    def handle(self, *args, **options):
        items = []
        packages = Package.objects.all()
        order_products = OrderProduct.objects.all()
        for i in range(0, 100000):
            number = generate_unique_id(i)
            package = random.choice(packages)
            order_product = random.choice(order_products)
            qty_weigh = order_product.qty + random.randint(-20, 20)
            crate_weight = random.randint(1, 6)
            items.append(PackageProduct(
                number=number,
                package=package,
                order_product=order_product,
                qty_weigh=qty_weigh,
                crate_weight=crate_weight
            ))
            msg = f'added packaged product{number},{package}, {qty_weigh}, {crate_weight}'
            print(msg)
        PackageProduct.objects.bulk_create(items)
