from django.db import models


# Create your models here.
class Bank(models.Model):
    name = models.CharField(max_length=200,
                            help_text='Name of the bank where cash from sales is deposited.List M-pesa paybill'
                                      ' here too.The bank name can not be removed from this list once there has been'
                                      ' cash deposit records added')

    def __str__(self):
        return self.name
