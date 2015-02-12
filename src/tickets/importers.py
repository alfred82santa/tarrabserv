import csv
from .models import TicketCode

__author__ = 'alfred'


class BaseImporter:
    label = 'Base importer'

    def __init__(self, csv_file=None):
        self.reader = None
        if csv_file:
            self.create_reader(csv_file)

    def create_reader(self, csv_file):
        self.reader = csv.reader(csv_file)

    def iter_tickets(self):
        for row in self.reader:
            ticket = TicketCode()
            self.map_to_ticket(ticket, row)
            yield ticket

    def map_to_ticket(self, ticket, row):
        ticket.code = row[0]
        ticket.ticket_number = row[2]
        ticket.status = row[3]
        ticket.external_id = row[8] or row[1]
        ticket.external_customer_name = row[9]
        ticket.external_fiscal_number = row[10]
        ticket.external_locator = row[11]


class ImporterManager:

    def __init__(self):
        self.importers = {}

    def register(self, name, importer_cls):
        self.importers[name] = importer_cls

    def unregister(self, name):
        del self.importers[name]

    def get_select_options(self):
        return ((name, cls.label) for name, cls in self.importers.items())

    def create_importer(self, name, csv_file):
        return self.importers[name](csv_file)


importer_manager = ImporterManager()


class DefaultImporter(BaseImporter):
    label = 'Tarrab.me'


importer_manager.register('tarrabme', DefaultImporter)


class AtrapaloImporter(BaseImporter):
    label = 'Atrapalo'

    def map_to_ticket(self, ticket, row):
        ticket.code = row[0]
        ticket.external_customer_name = row[1]
        ticket.external_fiscal_number = row[2]
        ticket.external_locator = row[3]
        ticket.external_id = row[4]


importer_manager.register('atrapalo', AtrapaloImporter)


class TicketeaImporter(BaseImporter):
    label = 'Ticketea'

    def map_to_ticket(self, ticket, row):
        ticket.code = row[0]
        ticket.external_locator = row[1]
        ticket.external_customer_name = row[2]


importer_manager.register('ticketea', TicketeaImporter)


class ProductesDeLaTerraImporter(BaseImporter):
    label = 'Productes de la terra'

    def map_to_ticket(self, ticket, row):
        ticket.code = row[0]
        ticket.external_customer_name = row[2]
        ticket.external_locator = row[3]


importer_manager.register('productesdelaterra', ProductesDeLaTerraImporter)
