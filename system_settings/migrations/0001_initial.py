# Generated by Django 2.0.3 on 2018-04-03 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_distribution', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.AggregationCenter')),
            ],
        ),
    ]
