from django import forms
from commons.adminForms import CommonAdminForm
from .models import TicketPack
from .importers import importer_manager

__author__ = 'alfred'


class TicketPackAdminForm(CommonAdminForm):
    upload_file_field = forms.FileField(label="Import file",
                                        required=False)
    upload_file_format_field = forms.ChoiceField(label="Import file format",
                                                 choices=importer_manager.get_select_options(),
                                                 required=False)
    generation_count = forms.IntegerField(label="Generate code count",
                                          min_value=1,
                                          max_value=100000,
                                          required=False)
    code_length = forms.IntegerField(label="Code length",
                                     min_value=10,
                                     max_value=40,
                                     required=False)

    class Meta(CommonAdminForm.Meta):
        model = TicketPack
