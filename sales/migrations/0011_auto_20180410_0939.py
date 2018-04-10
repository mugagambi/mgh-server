# Generated by Django 2.0.3 on 2018-04-10 06:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0010_bbf_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bbf',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='(-) are amounts the customer owes Meru Greens and (+) are amounts that Meru Greens owes thecustomer', max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashreceipt',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
