# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attempt',
            name='code',
        ),
        migrations.AlterField(
            model_name='ticketcode',
            name='external_customer_name',
            field=models.CharField(max_length=200, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ticketcode',
            name='external_fiscal_number',
            field=models.CharField(max_length=20, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ticketcode',
            name='external_id',
            field=models.CharField(max_length=50, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ticketcode',
            name='external_locator',
            field=models.CharField(max_length=40, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ticketcode',
            name='ticket_number',
            field=models.PositiveIntegerField(verbose_name='Ticket number', blank=True, null=True),
        ),
    ]
