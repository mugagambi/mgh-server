from django.core.management.base import BaseCommand
from faker import Faker

from core.models import AggregationCenter

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 10 fake aggregation centers'

    def handle(self, *args, **options):
        items = []
        for i in range(0, 10):
            name = 'center' + ' ' + str(i)
            location = fake.address()
            items.append(AggregationCenter(
                name=name,
                location=location
            ))
            msg = f'added center {name}, {location}'
            print(msg)
        AggregationCenter.objects.bulk_create(items)
