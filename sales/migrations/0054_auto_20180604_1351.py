# Generated by Django 2.0.3 on 2018-06-04 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0053_auto_20180602_1514'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='receipt',
            options={'ordering': ('date',), 'verbose_name': 'Sale', 'verbose_name_plural': 'Sales'},
        ),
    ]
