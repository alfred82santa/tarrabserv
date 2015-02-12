from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from commons.models import CommonModel


class Event(CommonModel):
    name = models.CharField(max_length=100, unique=True)
    commercial_name = models.CharField(max_length=150, unique=True)
    prefix = models.CharField(max_length=4, unique=True)
    start_date = models.DateTimeField(_('Start datetime'), blank=False, null=False, db_index=True)
    end_date = models.DateTimeField(_('End datetime'))
    active = models.BooleanField(default=False, editable=True)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
