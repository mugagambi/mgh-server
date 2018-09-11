from django.core.management.base import BaseCommand
from django.db.models import Sum
from faker import Faker

from sales.models import CustomerAccount, CustomerAccountBalance

fake = Faker('en_US')


class Command(BaseCommand):
    help = 'seed customer account balances'

    def handle(self, *args, **options):
        items = []
        accounts = CustomerAccount.objects.values('customer__id').annotate(total=Sum('amount'))
        for account in accounts:
            items.append(CustomerAccountBalance(
                customer_id=account['customer__id'],
                amount=account['total']
            ))
        CustomerAccountBalance.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS('seeded customer accounts balances'))
