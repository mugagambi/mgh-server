# Generated by Django 2.0.2 on 2018-02-05 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_crate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
    ]