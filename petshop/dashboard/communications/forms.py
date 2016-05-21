from django import forms

from oscar.apps.dashboard.communications.forms import (
    CommunicationEventTypeForm as OscarCommunicationEventTypeForm)


class CommunicationEventTypeForm(OscarCommunicationEventTypeForm):

    class Meta(OscarCommunicationEventTypeForm.Meta):
        fields = [
            'name', 'email_subject_template', 'email_body_template',
            'email_body_html_template', 'preview_order_number', 'preview_email',
            'staff'
        ]

    def __init__(self, *args, **kwargs):
        super(CommunicationEventTypeForm, self).__init__(*args, **kwargs)
        if getattr(self.instance, 'code', False) and not (
                'USER' in self.instance.code.split('_')):
                self.fields['staff'
                        ].label_from_instance = lambda obj: obj.email
        else:
            del self.fields['staff']
