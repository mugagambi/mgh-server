# Generated by Django 2.0.2 on 2018-03-05 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0022_auto_20180226_0946'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='receipt',
            options={'verbose_name': 'Sale', 'verbose_name_plural': 'Sales'},
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='name',
            new_name='Shop Name',
        ),
        migrations.AddField(
            model_name='customer',
            name='nick_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
