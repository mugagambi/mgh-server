# Generated by Django 2.0.3 on 2018-04-16 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20180407_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aggregationcenterproduct',
            name='qty',
            field=models.DecimalField(decimal_places=2, help_text='in kgs.', max_digits=8),
        ),
    ]
