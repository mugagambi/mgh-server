# Generated by Django 2.0.3 on 2018-04-08 19:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0009_auto_20180408_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='bbf',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.Customer'),
        ),
    ]
