# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-27 09:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('name', models.CharField(max_length=255, null=True, unique=True)),
                ('host', models.GenericIPAddressField()),
                ('usable', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'workers',
            },
        ),
    ]