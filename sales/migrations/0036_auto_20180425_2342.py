# Generated by Django 2.0.3 on 2018-04-25 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0035_customeraccount'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAccountBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=13)),
                ('customer', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.Customer')),
            ],
        ),
        migrations.AlterField(
            model_name='customeraccount',
            name='via',
            field=models.CharField(choices=[('M', 'M-pesa'), ('B', 'Bank Transfer'), ('C', 'Cash'), ('Q', 'Cheque')], max_length=1),
        ),
    ]
