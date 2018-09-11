import datetime
import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from sales.models import Receipt, ReceiptPayment

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake receipt payment'

    def handle(self, *args, **options):
        items = []
        for receipt in Receipt.objects.all():
            for i in range(0, 10):
                type = random.choice([1, 2, 3, 4, 5])
                amount = random.randint(1000, 100000)
                check_number = fake.uuid4()[:50] if type == 1 else ''
                transaction_id = fake.uuid4()[:15] if type == 2 else ''
                mobile_number = fake.phone_number()[:15] if type == 2 else ''
                date_to_pay = fake.date_time_between_dates(datetime_start=timezone.now() - datetime.timedelta(days=365),
                                                           datetime_end=timezone.now(),
                                                           tzinfo=None) if type == 4 else None
                transfer_code = fake.uuid4()[:50] if type == 5 else ''

                receipt = receipt
                items.append(ReceiptPayment(
                    type=type,
                    amount=amount,
                    check_number=check_number,
                    transaction_id=transaction_id,
                    date_to_pay=date_to_pay,
                    transfer_code=transfer_code,
                    receipt=receipt,
                    mobile_number=mobile_number
                ))
        ReceiptPayment.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS('seeded receipt payments'))
