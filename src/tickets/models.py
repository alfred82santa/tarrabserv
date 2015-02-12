from django.db import models
from django.conf import settings
from rest_framework import serializers
from commons.models import CommonModel
from events.models import Event, EventSerializer
from users.models import UserSerializer


MAX_CODE_LENGTH = 60
MAX_FAKE_CODE_LENGTH = MAX_CODE_LENGTH + 30


class TicketPack(CommonModel):
    name = models.CharField(max_length=50)
    prefix = models.CharField(max_length=2)

    event = models.ForeignKey(Event, related_name='ticket_packs')
    event.event_filter = True

    class Meta:
        unique_together = (('event', 'prefix'), ('event', 'name'))

    def get_prefix(self):
        return self.event.prefix + self.prefix

    def get_ticket_count(self):
        return self.ticket_codes.all().count()

    def __str__(self):
        return self.name + " for event " + self.event.name


class TicketPackSerializer(serializers.ModelSerializer):
    event = EventSerializer()

    class Meta:
        model = TicketPack


class TicketCodeManager(models.Manager):

    def get_for_attempt(self, code):
        if not code:
            raise TicketCode.DoesNotExist("Code is required")
        return self.get(code=code,
                        ticket_pack__event__active=True)

    def make_attempt(self, code, user):
        item = self.get_for_attempt(code=code)

        return item.make_attempt(user), item


class TicketCode(CommonModel):
    TICKET_CODE_STATUS_NEW = u'NW'
    TICKET_CODE_STATUS_USED = u'US'
    TICKET_CODE_STATUS_DISABLED = u'DS'
    TICKET_CODE_STATUS = (
        (TICKET_CODE_STATUS_NEW, u'New'),
        (TICKET_CODE_STATUS_USED, u'Used'),
        (TICKET_CODE_STATUS_DISABLED, u'Disabled')
    )
    code = models.CharField(max_length=MAX_CODE_LENGTH, unique=True)
    ticket_pack = models.ForeignKey(TicketPack, related_name='ticket_codes')
    status = models.CharField('status', max_length=2, choices=TICKET_CODE_STATUS, editable=False,
                              default=TICKET_CODE_STATUS_NEW)
    ticket_number = models.PositiveIntegerField('Ticket number', null=True)

    external_id = models.CharField(max_length=50, null=True)
    external_customer_name = models.CharField(max_length=200, null=True)
    external_fiscal_number = models.CharField(max_length=20, null=True)
    external_locator = models.CharField(max_length=40, null=True)

    objects = TicketCodeManager()

    class Meta:
        unique_together = (('ticket_pack', 'ticket_number'),
                           ('external_id', 'ticket_number'))

    def attempt_count(self):
        return self.attempt_list.count()

    def event(self):
        return self.ticket_pack.event

    def make_attempt(self, user):
        if self.status == TicketCode.TICKET_CODE_STATUS_DISABLED:
            return None

        at = Attempt(code=self.code,
                     success=False,
                     user=user,
                     ticket_code=self)
        at.save()

        first_attempt = self.attempt_list.order_by('id').all()[:1][0]
        if (self.status != TicketCode.TICKET_CODE_STATUS_USED) and (first_attempt.id == at.id):
            at.success = True
            at.save()
            self.status = TicketCode.TICKET_CODE_STATUS_USED
            self.user_last_modified = user
            self.save()

        return at

    def __str__(self):
        return self.code


class TicketCodeSerializer(serializers.ModelSerializer):
    ticket_pack = TicketPackSerializer()

    class Meta:
        model = TicketCode


class AbstractAttempt(models.Model):
    date = models.DateTimeField('attempt datetime', auto_now_add=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, None, models.ManyToOneRel, related_name="attempts_%(class)s")

    def save(self, force_insert=False, force_update=False, using=None, request=None):
        if request and request.user:
            self.user = request.user
        models.Model.save(self, force_insert, force_update, using)

    class Meta:
        abstract = True


class Attempt(AbstractAttempt):
    code = models.CharField(max_length=MAX_CODE_LENGTH)
    ticket_code = models.ForeignKey(TicketCode, editable=False, null=False,
                                    blank=False, related_name='attempt_list')
    success = models.BooleanField('Using success', default=False, editable=False)


class AttemptSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    ticket_code = TicketCodeSerializer()

    class Meta:
        model = Attempt
        depth = 1


class FakeAttempt(AbstractAttempt):
    code = models.CharField(max_length=MAX_FAKE_CODE_LENGTH)
