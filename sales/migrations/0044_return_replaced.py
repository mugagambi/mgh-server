# Generated by Django 2.0.3 on 2018-05-01 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0043_remove_cashreceiptpayment_date_to_pay'),
    ]

    operations = [
        migrations.AddField(
            model_name='return',
            name='replaced',
            field=models.BooleanField(default=False),
        ),
    ]