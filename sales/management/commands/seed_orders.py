import datetime
import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from core.models import User
from sales.models import Customer, Order
from utils import generate_unique_id

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake orders'

    def handle(self, *args, **options):
        items = []
        users = User.objects.all()
        customers = Customer.objects.all()
        for i in range(0, 1000):
            number = generate_unique_id(random.randint(0, 20))
            customer = random.choice(customers)
            received_by = random.choice(users)
            date_delivery = fake.date_time_between_dates(datetime_start=timezone.now() - datetime.timedelta(days=365),
                                                         datetime_end=timezone.now(), tzinfo=None)
            items.append(Order(
                number=number,
                customer=customer,
                received_by=received_by,
                date_delivery=date_delivery
            ))
        Order.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS('seeded orders'))
