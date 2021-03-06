# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-17 14:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('host', models.CharField(max_length=255)),
                ('free', models.BigIntegerField(null=True)),
                ('alive', models.BooleanField(db_index=True, default=True)),
            ],
            options={
                'db_table': 'nodes',
            },
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.TextField(db_index=True)),
                ('node', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cheapcdn.Node')),
            ],
            options={
                'db_table': 'objects',
            },
        ),
    ]
