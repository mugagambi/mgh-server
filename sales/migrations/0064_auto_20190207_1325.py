# Generated by Django 2.0.3 on 2019-02-07 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0063_auto_20190207_1059'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'permissions': (('view_customerstatement', 'can view customer statement'),)},
        ),
        migrations.AlterModelOptions(
            name='customeraccountbalance',
            options={'permissions': (('view_customeraccountbalance', 'view customer account balance'),)},
        ),
        migrations.AlterModelOptions(
            name='customerdeposit',
            options={'ordering': ('-date',), 'permissions': (('view_deposits', 'can view deposits'),)},
        ),
        migrations.AlterModelOptions(
            name='customerdiscount',
            options={'permissions': (('view_discounts', 'can view customer discounts'),)},
        ),
        migrations.AlterModelOptions(
            name='customerprice',
            options={'permissions': (('view_prices', 'can view prices'),)},
        ),
        migrations.AlterModelOptions(
            name='receipt',
            options={'ordering': ('-date',), 'permissions': (('view_receipts', 'can view receipts'),), 'verbose_name': 'Sale', 'verbose_name_plural': 'Sales'},
        ),
    ]
