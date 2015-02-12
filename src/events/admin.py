from django.contrib import admin
from commons.admin import CommonAdmin
from .adminForms import EventAdminForm
from .models import Event


class EventAdmin(CommonAdmin):
    form = EventAdminForm

    list_display = ('name', 'start_date', 'active', 'created_by')
    list_filter = ['active', 'start_date', 'created_by']
    search_fields = ['name', 'commercial_name']


admin.site.register(Event, EventAdmin)
