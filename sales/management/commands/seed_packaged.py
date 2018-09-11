import random

from django.core.management.base import BaseCommand
from faker import Faker

from core.models import User
from sales.models import Order, Package
from utils import generate_unique_id

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake packaged'

    def handle(self, *args, **options):
        items = []
        users = User.objects.all()
        orders = Order.objects.all()
        for i in range(0, 100000):
            number = generate_unique_id(random.randint(0, 20))
            order = random.choice(orders)
            packaged_by = random.choice(users)
            items.append(Package(
                number=number,
                order=order,
                packaged_by=packaged_by,
            ))
            msg = f'added packaged {number}, {order}, {packaged_by}'
            print(msg)
        Package.objects.bulk_create(items)
