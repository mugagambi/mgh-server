# Generated by Django 2.0.2 on 2018-02-08 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20180208_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='aggregationcenter',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]