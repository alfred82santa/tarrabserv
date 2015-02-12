from django import forms

__author__ = 'alfred'


class CommonAdminForm(forms.ModelForm):

    class Meta:
        exclude = ('created_by', 'modified_by')
