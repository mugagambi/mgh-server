# Generated by Django 2.0.3 on 2018-03-25 08:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BBF',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='CashReceipt',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('served_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CashReceiptParticular',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=8)),
                ('price', models.DecimalField(decimal_places=2, help_text='This is the unitprice for each quantity', max_digits=9)),
                ('discount', models.DecimalField(decimal_places=2, help_text='% discount', max_digits=5)),
                ('cash_receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.CashReceipt')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
            ],
        ),
        migrations.CreateModel(
            name='CashReceiptPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Cheque'), (2, 'Mpesa'), (3, 'Cash'), (4, 'Credit'), (5, 'Bank Transfer')])),
                ('check_number', models.CharField(blank=True, max_length=50)),
                ('transaction_id', models.CharField(blank=True, max_length=15)),
                ('mobile_number', models.CharField(blank=True, max_length=15)),
                ('date_to_pay', models.DateField(null=True)),
                ('transfer_code', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cash_receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.CashReceipt')),
            ],
        ),
        migrations.CreateModel(
            name='CreditSettlement',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('shop_name', models.CharField(max_length=100)),
                ('nick_name', models.CharField(blank=True, max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerDiscount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.DecimalField(decimal_places=2, help_text='% discount', max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Customer')),
                ('product', models.ForeignKey(help_text='search by product name', on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, help_text='This is the unitprice for each quantity', max_digits=9)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(help_text='search by customer no. , shop name or nick name', on_delete=django.db.models.deletion.CASCADE, to='sales.Customer')),
                ('product', models.ForeignKey(help_text='search by product name', on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('date_delivery', models.DateField(blank=True, null=True, verbose_name='date of delivery')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(help_text='search by customer no. , shop name or nick name', on_delete=django.db.models.deletion.CASCADE, to='sales.Customer')),
                ('received_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderDistributionPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=8)),
                ('center', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.AggregationCenter')),
            ],
        ),
        migrations.CreateModel(
            name='OrderlessParticular',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=8)),
                ('price', models.DecimalField(decimal_places=2, help_text='This is the unitprice for each quantity', max_digits=9)),
                ('discount', models.DecimalField(decimal_places=2, help_text='% discount', max_digits=5, null=True)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Product')),
            ],
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('qty', models.DecimalField(decimal_places=2, max_digits=8)),
                ('discount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.CustomerDiscount')),
                ('order', models.ForeignKey(help_text='search by order no.', on_delete=django.db.models.deletion.CASCADE, to='sales.Order')),
                ('price', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.CustomerPrice')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
            ],
            options={
                'verbose_name': 'Order Report',
                'verbose_name_plural': 'Order Reports',
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Order')),
                ('packaged_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PackageProduct',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('qty_weigh', models.DecimalField(decimal_places=2, max_digits=8)),
                ('crate_weight', models.DecimalField(decimal_places=2, max_digits=4)),
                ('order_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.OrderProduct')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Package')),
            ],
            options={
                'verbose_name_plural': 'Packed Products',
            },
        ),
        migrations.CreateModel(
            name='PackageProductCrate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crate', models.ForeignKey(help_text='search by crate number', on_delete=django.db.models.deletion.CASCADE, to='core.Crate', to_field='number')),
                ('package_product', models.ForeignKey(help_text='search package item', on_delete=django.db.models.deletion.CASCADE, to='sales.PackageProduct')),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Customer')),
                ('served_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Sale',
                'verbose_name_plural': 'Sales',
            },
        ),
        migrations.CreateModel(
            name='ReceiptParticular',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.DecimalField(decimal_places=2, max_digits=8)),
                ('price', models.DecimalField(decimal_places=2, help_text='This is the unitprice for each quantity', max_digits=9)),
                ('discount', models.DecimalField(decimal_places=2, help_text='% discount', max_digits=5, null=True)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Receipt')),
            ],
        ),
        migrations.CreateModel(
            name='ReceiptPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Cheque'), (2, 'Mpesa'), (3, 'Cash'), (4, 'Credit'), (5, 'Bank Transfer')])),
                ('check_number', models.CharField(blank=True, max_length=50)),
                ('transaction_id', models.CharField(blank=True, max_length=15)),
                ('mobile_number', models.CharField(blank=True, max_length=15)),
                ('date_to_pay', models.DateField(null=True)),
                ('transfer_code', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Receipt')),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Reject',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('qty', models.DecimalField(decimal_places=2, max_digits=8)),
                ('description', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('refund_qty', models.DecimalField(decimal_places=2, max_digits=8, null=True)),
                ('refund_date', models.DateTimeField(null=True)),
                ('customer', models.ForeignKey(help_text='search by customer number, shop name and nick name', on_delete=django.db.models.deletion.CASCADE, to='sales.Customer')),
                ('product', models.ForeignKey(help_text='search by product name', on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Receipt')),
            ],
        ),
        migrations.CreateModel(
            name='Return',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('qty', models.DecimalField(decimal_places=2, max_digits=8)),
                ('description', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('customer', models.ForeignKey(help_text='search by customer number, shop name and nick name', on_delete=django.db.models.deletion.CASCADE, to='sales.Customer')),
                ('product', models.ForeignKey(help_text='search product name', on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
                ('receipt', models.ForeignKey(help_text='search receipt no', on_delete=django.db.models.deletion.CASCADE, to='sales.Receipt')),
            ],
        ),
        migrations.CreateModel(
            name='SalesCrate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_issued', models.DateField()),
                ('date_returned', models.DateField(null=True)),
                ('agent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('crate', models.ForeignKey(help_text='search by crate number', on_delete=django.db.models.deletion.CASCADE, to='core.Crate', to_field='number')),
                ('held_by', models.ForeignKey(help_text='search by customer no. , shop name or nick name', null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.Customer')),
            ],
        ),
        migrations.AddField(
            model_name='orderlessparticular',
            name='receipt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Receipt'),
        ),
        migrations.AddField(
            model_name='orderdistributionpoint',
            name='order_product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.OrderProduct'),
        ),
        migrations.AddField(
            model_name='customer',
            name='region',
            field=models.ForeignKey(help_text='search by region name', on_delete=django.db.models.deletion.CASCADE, to='sales.Region'),
        ),
        migrations.AddField(
            model_name='creditsettlement',
            name='receipt',
            field=models.ForeignKey(help_text='search by receipt no.', on_delete=django.db.models.deletion.CASCADE, to='sales.Receipt'),
        ),
        migrations.AddField(
            model_name='creditsettlement',
            name='served_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bbf',
            name='customer',
            field=models.ForeignKey(help_text='search by customer number, shop name and nick name', on_delete=django.db.models.deletion.CASCADE, to='sales.Customer'),
        ),
        migrations.AddField(
            model_name='bbf',
            name='receipt',
            field=models.ForeignKey(help_text='search by receipt no.', on_delete=django.db.models.deletion.CASCADE, to='sales.Receipt'),
        ),
        migrations.CreateModel(
            name='Invoices',
            fields=[
            ],
            options={
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
                'proxy': True,
                'indexes': [],
            },
            bases=('sales.receipt',),
        ),
        migrations.AlterUniqueTogether(
            name='customerprice',
            unique_together={('customer', 'product')},
        ),
        migrations.AlterUniqueTogether(
            name='customerdiscount',
            unique_together={('customer', 'product')},
        ),
    ]
