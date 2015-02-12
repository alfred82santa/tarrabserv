import datetime
from django.db import transaction
from django.contrib import admin, messages
from django.contrib.auth.models import Group, Permission
from commons.admin import CommonAdmin
from .adminForms import TicketPackAdminForm
from .models import TicketCode, TicketPack
from .importers import importer_manager
from .helpers import create_code
from tickets.exporters import ticket_exporter_manager, ticket_pack_exporter_manager


class TicketCodeAdmin(CommonAdmin):
    list_display = ['code', 'ticket_number', 'status', 'ticket_pack', 'attempt_count', 'event',
                    'external_customer_name', 'external_fiscal_number', 'external_locator', 'external_id']
    list_filter = ['ticket_pack__event', 'status', 'ticket_pack']
    actions = ['disable',
               'remove_attempts',
               'mark_as_used',
               'mark_as_new',
               'make_attempt'] + list(ticket_exporter_manager.exporters)
    search_fields = ['code', 'ticket_number', 'external_locator', 'external_id']

    form = TicketPackAdminForm

    list_per_page = 500

    def disable(self, request, queryset):
        queryset.update(status=TicketCode.TICKET_CODE_STATUS_DISABLED,
                        modified_by=request.user,
                        modified_date=datetime.datetime.now())

    def mark_as_used(self, request, queryset):
        queryset.update(status=TicketCode.TICKET_CODE_STATUS_USED,
                        modified_by=request.user,
                        modified_date=datetime.datetime.now())

    def mark_as_new(self, request, queryset):
        self.remove_attempts(request, queryset)
        queryset.update(status=TicketCode.TICKET_CODE_STATUS_NEW,
                        modified_by=request.user,
                        modified_date=datetime.datetime.now())

    def make_attempt(self, request, queryset):
        for ti in queryset:
            with transaction.atomic():
                ti.make_attempt(request.user)

    def remove_attempts(self, request, queryset):
        for ti in queryset:
            ti.attempt_list.filter().delete()


admin.site.register(TicketCode, TicketCodeAdmin)


class TicketPackAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'event', 'get_ticket_count', ]
    list_filter = ['event', ]
    actions = ['put_ticket_number'] + list(ticket_pack_exporter_manager.exporters)

    form = TicketPackAdminForm

    fieldsets = (
        (None, {
            'fields': ('name', 'event', 'prefix')
        }),
        ('Generate ticket codes', {
            'classes': ('collapse',),
            'fields': ('generation_count', 'code_length')
        }),
        ('Upload ticket codes', {
            'classes': ('collapse',),
            'fields': ('upload_file_field', 'upload_file_format_field',)
        }),
    )

    def save_model(self, request, obj, form, change):
        super(TicketPackAdmin, self).save_model(request, obj, form, change)

        if "upload_file_field" in request.FILES:
            self.process_upload_field(obj, request,
                                      request.FILES["upload_file_field"],
                                      form.cleaned_data['upload_file_format_field'])
        elif form.cleaned_data['generation_count'] and form.cleaned_data['code_length']:
            self.generate_codes(obj, request,
                                form.cleaned_data['generation_count'],
                                form.cleaned_data['code_length'])

    def process_upload_field(self, ticket_pack, request,
                             up_file, importer):
        reader = importer_manager.create_importer(importer, up_file)

        for ticket in reader.iter_tickets():
            ticket.ticket_pack = ticket_pack

            ticket.created_by = request.user
            ticket.modified_by = request.user
            try:
                ticket.save()
            except Exception as ex:
                messages.warning(request,
                                 "Error inserting code '%s' (line %d): %s" % (ticket.code,
                                                                              reader.reader.line_num,
                                                                              ex))

    def generate_codes(self, ticket_pack, request, count, length=14):
        for i in range(count):
            ticket_code = TicketCode(ticket_pack=ticket_pack,
                                     created_by=request.user,
                                     modified_by=request.user)
            created = False
            while not created:
                try:
                    ticket_code.code = create_code(length, ticket_pack.get_prefix())
                    with transaction.atomic():
                        ticket_code.save()
                    created = True
                except:
                    pass

    def put_ticket_number(self, request, queryset):
        try:
            max_num_ticket = TicketCode.objects.order_by('-ticket_number').filter(ticket_pack__in=queryset)[:1][0]
        except IndexError:
            return

        index = max_num_ticket.ticket_number or 0
        tickets = TicketCode.objects.filter(ticket_pack__in=queryset, ticket_number=None).all()
        for ticket in tickets:
            index += 1
            ticket.ticket_number = index
            ticket.user_last_modified = request.user
            with transaction.atomic():
                ticket.save()

    put_ticket_number.short_description = "Put ticket number to every ticket code selected"

admin.site.register(TicketPack, TicketPackAdmin)

new_group, created = Group.objects.get_or_create(name='Gatekeeper')
permission = Permission.objects.get(codename='tickets.add_attempt')
new_group.permissions.add(permission)
