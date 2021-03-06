# Generated by Django 3.1.3 on 2020-11-08 01:16

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_number', models.CharField(db_index=True, max_length=40, verbose_name='part number')),
                ('part_type', models.CharField(choices=[('Part', 'Part'), ('Accessory', 'Accessory')], default='Part', max_length=16, verbose_name='type')),
                ('cost_price_range', models.CharField(choices=[('0-50', '0-50'), ('50-100', '50-100'), ('100-150', '100-150'), ('150-200', '150-200')], default='0-50', max_length=16, verbose_name='type')),
                ('manufacturer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='parts.manufacturer', verbose_name='manufacturer')),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain_name', models.CharField(db_index=True, max_length=40, verbose_name='domain name')),
                ('is_client', models.BooleanField(default=False, verbose_name='is client')),
                ('start_date', models.DateField(default=datetime.date.today, verbose_name='start date')),
                ('manufacturers', models.ManyToManyField(to='parts.Manufacturer', verbose_name='manufacturers')),
            ],
        ),
        migrations.CreateModel(
            name='PartPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, verbose_name='date')),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='price')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='part_prices', to='parts.part', verbose_name='part')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='part_prices', to='parts.website', verbose_name='website')),
            ],
        ),
        migrations.CreateModel(
            name='PartCostPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(db_index=True, verbose_name='start date')),
                ('cost', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='cost')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='part_cost_points', to='parts.part', verbose_name='part')),
            ],
        ),
    ]
