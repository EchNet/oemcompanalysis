# Generated by Django 3.1.3 on 2020-11-24 23:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0007_auto_20201120_0549'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadprogress',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='created at'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploadprogress',
            name='type',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='type'),
        ),
        migrations.AddField(
            model_name='uploadprogress',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='updated at'),
        ),
    ]