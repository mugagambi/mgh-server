# Generated by Django 2.0.3 on 2018-03-07 16:05

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sales', '0025_receiptparticular_total'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleSummary',
            fields=[
            ],
            options={
                'verbose_name': 'Sale Summary',
                'verbose_name_plural': 'Sales Summary',
                'proxy': True,
                'indexes': [],
            },
            bases=('sales.receiptparticular',),
        ),
    ]
