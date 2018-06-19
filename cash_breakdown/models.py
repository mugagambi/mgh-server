from django.db import models

# Create your models here.
from django.utils.timezone import now


class Bank(models.Model):
    name = models.CharField(max_length=200,
                            help_text='Name of the bank where cash from sales is deposited.List M-pesa paybill'
                                      ' here too.The bank name can not be removed from this list once there has been'
                                      ' cash deposit records added')

    def __str__(self):
        return self.name


class CashDeposit(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=15)
    date = models.DateField(default=now)

    def __str__(self):
        str(self.amount) + ' deposit ' + str(self.bank)
