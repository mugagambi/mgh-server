# Generated by Django 2.0.2 on 2018-02-08 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0020_auto_20180207_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone_number',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]