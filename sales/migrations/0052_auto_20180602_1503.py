# Generated by Django 2.0.3 on 2018-06-02 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0051_billedtogether_billedtogethercustomer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billedtogether',
            name='box',
            field=models.CharField(max_length=100, verbose_name='P.O Box'),
        ),
    ]
