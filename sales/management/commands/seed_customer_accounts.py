from django.core.management.base import BaseCommand

from sales.models import ReceiptParticular, CustomerAccount, ReceiptPayment
from utils import main_generate_unique_id


class Command(BaseCommand):
    help = 'generate 100000 fake customer accounts'

    def handle(self, *args, **options):
        items = []
        for instance in ReceiptParticular.objects.all():
            items.append(CustomerAccount(number=main_generate_unique_id()[:10],
                                         customer=instance.receipt.customer,
                                         amount=-instance.total,
                                         date=instance.receipt.date,
                                         type='P',
                                         receipt=instance.receipt))
        for instance in ReceiptPayment.objects.all():
            if instance.type == 1:
                type = 'Q'
                cheque_number = instance.check_number
                transaction_id = ''
                phone_number = ''
            elif instance.type == 2:
                type = 'M'
                cheque_number = ''
                transaction_id = instance.transaction_id
                phone_number = instance.mobile_number
            elif instance.type == 3:
                type = 'C'
                cheque_number = ''
                transaction_id = ''
                phone_number = ''
            elif instance.type == 5:
                type = 'B'
                cheque_number = ''
                transaction_id = ''
                phone_number = ''
            else:
                type = ''
                cheque_number = ''
                transaction_id = ''
                phone_number = ''
            if instance.type != 4:
                items.append(CustomerAccount(number=main_generate_unique_id()[:10],
                                             customer=instance.receipt.customer,
                                             amount=instance.amount,
                                             date=instance.receipt.date,
                                             type='A',
                                             via=type,
                                             receipt=instance.receipt,
                                             cheque_number=cheque_number,
                                             transaction_id=transaction_id,
                                             phone_number=phone_number))
        CustomerAccount.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS('seeded customer accounts'))
