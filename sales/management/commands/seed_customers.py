import random

from django.core.management.base import BaseCommand
from faker import Faker

from core.models import User
from sales.models import Region, Customer
from utils import generate_unique_id

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 1000 fake customers'

    def handle(self, *args, **options):
        items = []
        regions = Region.objects.all()
        users = User.objects.all()
        for i in range(0, 1000):
            number = generate_unique_id(random.randint(0, 20))
            shop_name = 'shop_name ' + ' ' + str(i)
            nick_name = 'nickname ' + str(i)
            location = fake.address()
            added_by = random.choice(users)
            region = random.choice(regions)
            items.append(Customer(
                shop_name=shop_name,
                nick_name=nick_name,
                number=number,
                location=location,
                added_by=added_by,
                region=region
            ))
            msg = f'added customer {number}, {shop_name}, {nick_name}, {location}, {added_by}, {region}'
            print(msg)
        Customer.objects.bulk_create(items)
