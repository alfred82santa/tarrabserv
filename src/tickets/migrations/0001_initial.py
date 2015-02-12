# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attempt',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateTimeField(verbose_name='attempt datetime', auto_now_add=True)),
                ('code', models.CharField(max_length=60)),
                ('success', models.BooleanField(editable=False, verbose_name='Using success', default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FakeAttempt',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateTimeField(verbose_name='attempt datetime', auto_now_add=True)),
                ('code', models.CharField(max_length=90)),
                ('user', models.ForeignKey(related_name='attempts_fakeattempt', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketCode',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creation_date', models.DateTimeField(verbose_name='creation datetime', auto_now_add=True)),
                ('modified_date', models.DateTimeField(verbose_name='modified datetime', auto_now=True)),
                ('code', models.CharField(unique=True, max_length=60)),
                ('status', models.CharField(editable=False, choices=[('NW', 'New'), ('US', 'Used'), ('DS', 'Disabled')], verbose_name='status', max_length=2, default='NW')),
                ('ticket_number', models.PositiveIntegerField(null=True, verbose_name='Ticket number')),
                ('external_id', models.CharField(null=True, max_length=50)),
                ('external_customer_name', models.CharField(null=True, max_length=200)),
                ('external_fiscal_number', models.CharField(null=True, max_length=20)),
                ('external_locator', models.CharField(null=True, max_length=40)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='created_tickets_ticketcode', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='modification_tickets_ticketcode', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketPack',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('creation_date', models.DateTimeField(verbose_name='creation datetime', auto_now_add=True)),
                ('modified_date', models.DateTimeField(verbose_name='modified datetime', auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('prefix', models.CharField(max_length=2)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='created_tickets_ticketpack', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(related_name='ticket_packs', to='events.Event')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='modification_tickets_ticketpack', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='ticketpack',
            unique_together=set([('event', 'prefix'), ('event', 'name')]),
        ),
        migrations.AddField(
            model_name='ticketcode',
            name='ticket_pack',
            field=models.ForeignKey(related_name='ticket_codes', to='tickets.TicketPack'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='ticketcode',
            unique_together=set([('external_id', 'ticket_number'), ('ticket_pack', 'ticket_number')]),
        ),
        migrations.AddField(
            model_name='attempt',
            name='ticket_code',
            field=models.ForeignKey(editable=False, related_name='attempt_list', to='tickets.TicketCode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attempt',
            name='user',
            field=models.ForeignKey(related_name='attempts_attempt', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
