# Generated by Django 2.0.3 on 2018-04-07 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_auto_20180407_0020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashreceiptpayment',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Mpesa'), (2, 'Cash')]),
        ),
    ]
