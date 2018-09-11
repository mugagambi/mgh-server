import random

from django.core.management.base import BaseCommand
from faker import Faker

from sales.models import CashReceipt, CashReceiptPayment

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'generate 100000 fake cash receipt payment'

    def handle(self, *args, **options):
        items = []
        for receipt in CashReceipt.objects.all():
            for i in range(0, 10):
                type = random.choice([1, 2])
                amount = random.randint(1000, 100000)
                transaction_id = fake.uuid4()[:15] if type == 2 else ''
                mobile_number = fake.phone_number()[:15] if type == 2 else ''
                receipt = receipt
                items.append(CashReceiptPayment(
                    type=type,
                    amount=amount,
                    transaction_id=transaction_id,
                    cash_receipt=receipt,
                    mobile_number=mobile_number
                ))
                msg = f'added cash receipt payment {type}, {amount},' \
                      f' {transaction_id}, {mobile_number}, {receipt}'
                print(msg)
        CashReceiptPayment.objects.bulk_create(items)
