# Generated by Django 2.0.3 on 2019-03-08 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0062_auto_20180911_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='number',
            field=models.CharField(max_length=53, primary_key=True, serialize=False, unique=True),
        ),
    ]
