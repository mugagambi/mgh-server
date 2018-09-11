import datetime
import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from core.models import Product
from sales.models import OrderlessPackage
from utils import generate_unique_id

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake orderless package'

    def handle(self, *args, **options):
        items = []
        products = Product.objects.all()
        for i in range(0, 1000):
            number = generate_unique_id(random.randint(0, 20))
            product = random.choice(products)
            qty = random.randint(500, 10000)
            date = fake.date_time_between_dates(datetime_start=timezone.now() - datetime.timedelta(days=365),
                                                datetime_end=timezone.now(), tzinfo=None)
            items.append(OrderlessPackage(
                number=number,
                product=product,
                qty=qty,
                date=date
            ))
        OrderlessPackage.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS('seeded orderless package'))
