# Generated by Django 2.0.3 on 2018-05-27 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0046_auto_20180527_0937'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='return',
            options={'ordering': ('-date',)},
        ),
        migrations.AlterField(
            model_name='customerdeposit',
            name='cheque_number',
            field=models.CharField(blank=True, help_text='Provide cheque number if the  the deposit was received via Cheque', max_length=100),
        ),
        migrations.AlterField(
            model_name='customerdeposit',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Provide phone number if the  the deposit was received via mpesa', max_length=10),
        ),
        migrations.AlterField(
            model_name='customerdeposit',
            name='transaction_id',
            field=models.CharField(blank=True, help_text='Provide transaction Id if the  the deposit was received via bank transfer', max_length=10),
        ),
    ]