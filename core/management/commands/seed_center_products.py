import datetime
import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from core.models import AggregationCenter, Product, AggregationCenterProduct

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100k center products'

    def handle(self, *args, **options):
        centers = AggregationCenter.objects.all()
        products = Product.objects.all()
        items = []
        for i in range(0, 100000):
            aggregation_center = random.choice(centers)
            product = random.choice(products)
            qty = random.randint(0, 1000)
            date = fake.date_time_between_dates(datetime_start=timezone.now() - datetime.timedelta(days=365),
                                                datetime_end=timezone.now(), tzinfo=None)
            items.append(AggregationCenterProduct(
                aggregation_center=aggregation_center,
                product=product,
                qty=qty,
                date=date
            ))
            msg = f'added aggregation center product {aggregation_center}, {product}, {qty}, {date}'
            print(msg)
        AggregationCenterProduct.objects.bulk_create(items)
