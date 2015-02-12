# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('creation_date', models.DateTimeField(verbose_name='creation datetime', auto_now_add=True)),
                ('modified_date', models.DateTimeField(verbose_name='modified datetime', auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('commercial_name', models.CharField(max_length=150, unique=True)),
                ('prefix', models.CharField(max_length=4, unique=True)),
                ('start_date', models.DateTimeField(verbose_name='Start datetime', db_index=True)),
                ('end_date', models.DateTimeField(verbose_name='End datetime')),
                ('active', models.BooleanField(default=False)),
                ('description', models.TextField(default='', blank=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='created_events_event', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='modification_events_event', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
