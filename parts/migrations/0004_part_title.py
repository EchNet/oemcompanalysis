# Generated by Django 3.1.3 on 2020-11-11 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0003_auto_20201111_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='title',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='title'),
        ),
    ]