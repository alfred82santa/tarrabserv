from commons.adminForms import CommonAdminForm
from .models import Event

__author__ = 'alfred'


class EventAdminForm(CommonAdminForm):

    class Meta(CommonAdminForm.Meta):
        model = Event
