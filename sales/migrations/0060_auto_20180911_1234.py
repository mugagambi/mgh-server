# Generated by Django 2.0.3 on 2018-09-11 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0059_auto_20180619_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeraccount',
            name='number',
            field=models.CharField(max_length=53, primary_key=True, serialize=False, unique=True),
        ),
    ]
