# Generated by Django 2.0.3 on 2018-06-04 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0054_auto_20180604_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerdeposit',
            name='remaining_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]