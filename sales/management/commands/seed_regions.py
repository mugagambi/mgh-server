from django.core.management.base import BaseCommand
from faker import Faker

from sales.models import Region

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 50 fake regions'

    def handle(self, *args, **options):
        items = []
        for i in range(0, 50):
            name = 'region ' + str(i)
            items.append(Region(
                name=name,
            ))
        Region.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS('seeded regions'))
