# Generated by Django 2.0.2 on 2018-02-05 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_grade'),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregationCenter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AggregationCenterProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('aggregation_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.AggregationCenter')),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='active',
        ),
        migrations.AddField(
            model_name='aggregationcenterproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Product'),
        ),
    ]