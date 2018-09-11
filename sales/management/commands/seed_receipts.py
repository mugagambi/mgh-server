import datetime
import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from pytz import timezone as pytz_zone

from core.models import User
from sales.models import Customer, Receipt
from utils import generate_unique_id

fake = Faker('en_US')

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


class Command(BaseCommand):
    help = 'generate 100000 fake orders'

    def handle(self, *args, **options):
        items = []
        users = User.objects.all()
        customers = Customer.objects.all()
        for i in range(0, 10000):
            number = generate_unique_id(random.randint(0, 20))[:10]
            customer = random.choice(customers)
            served_by = random.choice(users)
            bbf_balance = random.randint(0, 10000)
            balance = random.randint(0, 10000)
            date = fake.date_time_between_dates(datetime_start=timezone.now() - datetime.timedelta(days=365),
                                                datetime_end=timezone.now(), tzinfo=AFRICA_NAIROBI)
            items.append(Receipt(
                number=number,
                customer=customer,
                served_by=served_by,
                date=date,
                bbf_balance=bbf_balance,
                balance=balance
            ))
        Receipt.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS('seeded receipts'))
