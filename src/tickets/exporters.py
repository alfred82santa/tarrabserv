import csv
from django.http.response import HttpResponse
from .models import TicketCode

__author__ = 'alfred'


class BaseExporter:
    short_description = 'Base class for exporters'
    mime_type = 'text/csv'

    @property
    def __name__(self):
        return self.__class__.__name__

    def __call__(self, modeladmin, request, queryset, filename='export'):
        response = self.create_response()
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)

        tickets = self.get_tickets(queryset)

        self.write_data(response, tickets)

        return response

    def create_response(self):
        return HttpResponse(content_type=self.mime_type)

    def write_data(self, response, tickets):
        pass

    def get_tickets(self, queryset):
        return queryset


class BaseTicketExporter(BaseExporter):
    short_description = 'Base class for ticket exporters'

    def get_tickets(self, queryset):
        return queryset.order_by('ticket_number')


class BaseTicketPackExporter(BaseExporter):
    short_description = 'Base class for ticket pack exporters'

    def get_tickets(self, queryset):
        return TicketCode.objects.order_by('-ticket_number').filter(ticket_pack__in=queryset)


class ExporterManager:

    def __init__(self):
        self.exporters = set()

    def register(self, exporter_cls):
        self.exporters.add(exporter_cls)

    def unregister(self, exporter_cls):
        self.exporters.remove(exporter_cls)


ticket_exporter_manager = ExporterManager()
ticket_pack_exporter_manager = ExporterManager()


class DefaultTicketExporter(BaseTicketExporter):
    short_description = 'Export selected tickets as CSV file'

    def write_data(self, response, tickets):
        writer = self.create_writer(response)
        row = ['code',
               'ticket_id',
               'ticket_number',
               'status',
               'creation_date',
               'modified_date',
               'modified_by',
               'ticket_pack',
               'external_id',
               'external_customer_name',
               'external_fiscal_number',
               'external_locator',
               'attempt_count']

        writer.writerow(row)

        for item in tickets:
            self.write_item(writer, item)

    def write_item(self, writer, item):
        row = [str(item.code),
               "{num:06d}".format(num=item.id),
               "{num:05d}".format(num=int(item.ticket_number))
               if item.ticket_number is not None else '',
               item.status,
               str(item.creation_date),
               str(item.modified_date),
               str(item.modified_by),
               str(item.ticket_pack),
               item.external_id,
               item.external_customer_name,
               item.external_fiscal_number,
               item.external_locator,
               item.attempt_count()]

        writer.writerow(row)

    def create_writer(self, response):
        return csv.writer(response)


class DefaultTicketWithAttemptsExporter(DefaultTicketExporter):
    short_description = 'Export selected tickets with attempts as CSV file'

    def write_item(self, writer, item):
        super(DefaultTicketWithAttemptsExporter, self).write_item(writer, item)

        attempts = item.attempt_list.order_by('date').all()

        for attempt in attempts:
            row = ['',
                   attempt.id,
                   attempt.code,
                   str(attempt.success),
                   str(attempt.date),
                   '',
                   str(attempt.user)]

            writer.writerow(row)


ticket_exporter_manager.register(DefaultTicketExporter())
ticket_exporter_manager.register(DefaultTicketWithAttemptsExporter())


class DefaultTicketPackExporter(BaseTicketPackExporter, DefaultTicketExporter):
    short_description = 'Export selected ticket packs as CSV file'


class DefaultTicketPackWithAttemptsExporter(BaseTicketPackExporter,
                                            DefaultTicketWithAttemptsExporter):
    short_description = 'Export selected ticket packs with attempts as CSV file'

ticket_pack_exporter_manager.register(DefaultTicketPackExporter())
ticket_pack_exporter_manager.register(DefaultTicketPackWithAttemptsExporter())
