# Generated by Django 2.0.3 on 2018-05-31 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0049_auto_20180531_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customertotaldiscount',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sales.Customer'),
        ),
        migrations.AlterUniqueTogether(
            name='customertotaldiscount',
            unique_together=set(),
        ),
    ]