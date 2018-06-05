from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from sales.models import ReceiptPayment, Receipt
from tooling.models import Commands


class Command(BaseCommand):
    command = 'update_credit_payment'
    help = 'Help update credit payment balance for a system already in production.Runs once'

    def handle(self, *args, **options):
        command, created = Commands.objects.get_or_create(command=self.command,
                                                          defaults={
                                                              'runs': 'O'
                                                          })
        if not created and command.run_times >= 1:
            raise CommandError('This command can\'t be run more than once')
        else:
            payments = ReceiptPayment.objects.filter(type=4)
            receipt_ids = [payment.receipt.pk for payment in payments]
            receipts_qs = Receipt.objects.filter(number__in=receipt_ids, settled=False)
            receipts = receipts_qs.annotate(amount=Sum('receiptparticular__total'))
            for receipt in receipts:
                receipt.balance = receipt.amount
                receipt.save()
            command.run_times = command.run_times + 1
            command.save()
            self.stdout.write(self.style.SUCCESS('Credit payment balances have been updated successfully'))
