# Generated by Django 2.0.2 on 2018-02-03 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_product_active'),
        ('sales', '0007_customerprice'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerDiscounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.DecimalField(decimal_places=2, help_text='% discount', max_digits=5)),
                ('grade', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.Customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
            ],
        ),
    ]
