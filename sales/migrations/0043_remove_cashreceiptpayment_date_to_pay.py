# Generated by Django 2.0.3 on 2018-05-01 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0042_auto_20180426_1458'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cashreceiptpayment',
            name='date_to_pay',
        ),
    ]
