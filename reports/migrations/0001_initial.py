# Generated by Django 2.0.3 on 2018-03-11 13:34

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleSummary',
            fields=[
            ],
            options={
                'verbose_name': 'Outwards Stocks Summary',
                'verbose_name_plural': 'Outwards Stocks Summary',
                'proxy': True,
                'indexes': [],
            },
            bases=('sales.receiptparticular',),
        ),
    ]