from django.core.management.base import BaseCommand, CommandError
from django.db.models import F

from sales.models import CustomerDeposit
from tooling.models import Commands


class Command(BaseCommand):
    command = 'update_remaining_deposit'
    help = 'Help update the remaining deposit amount in a system that has already gone to production.Runs once'

    def handle(self, *args, **options):
        command, created = Commands.objects.get_or_create(command=self.command,
                                                          defaults={
                                                              'runs': 'O'
                                                          })
        if not created and command.run_times >= 1:
            raise CommandError('This command can\'t be run more than once')
        else:
            try:
                CustomerDeposit.objects.all().update(remaining_amount=F('amount'))
                command.run_times = command.run_times + 1
                command.save()
                self.stdout.write(self.style.SUCCESS('Deposits have been updated successfully'))
            except Exception:
                raise CommandError('An error occurred when updating deposits.The error %s', Exception)
