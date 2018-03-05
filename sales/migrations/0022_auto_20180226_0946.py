# Generated by Django 2.0.2 on 2018-02-26 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0021_auto_20180208_1638'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderproducts',
            options={'verbose_name': 'Order Report', 'verbose_name_plural': 'Order Reports'},
        ),
        migrations.AlterModelOptions(
            name='packageproduct',
            options={'verbose_name_plural': 'Packed Products'},
        ),
        migrations.RemoveField(
            model_name='cashreceiptparticular',
            name='grade',
        ),
        migrations.RemoveField(
            model_name='customerdiscount',
            name='grade',
        ),
        migrations.RemoveField(
            model_name='customerprice',
            name='grade',
        ),
        migrations.RemoveField(
            model_name='orderproducts',
            name='grade',
        ),
        migrations.RemoveField(
            model_name='packageproduct',
            name='grade',
        ),
        migrations.RemoveField(
            model_name='receiptparticular',
            name='grade',
        ),
        migrations.RemoveField(
            model_name='returnsorrejects',
            name='grade',
        ),
        migrations.AlterField(
            model_name='order',
            name='date_delivery',
            field=models.DateField(blank=True, null=True, verbose_name='date of delivery'),
        ),
    ]