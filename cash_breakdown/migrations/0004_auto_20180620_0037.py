# Generated by Django 2.0.3 on 2018-06-19 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_breakdown', '0003_cashexpense'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashexpense',
            name='narration',
            field=models.TextField(help_text='e.g, KAR Fuel'),
        ),
    ]