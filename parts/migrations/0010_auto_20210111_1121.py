# Generated by Django 3.1.3 on 2021-01-11 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0009_auto_20201201_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='for_testing',
            field=models.BooleanField(default=False, verbose_name='for testing'),
        ),
        migrations.AddField(
            model_name='website',
            name='for_testing',
            field=models.BooleanField(default=False, verbose_name='for testing'),
        ),
    ]
