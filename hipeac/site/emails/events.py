from django.template.defaultfilters import date as date_filter
from typing import List


class TemplateEmail:
    template_key_legacy = None
    template = None
    from_email = 'HiPEAC <management@hipeac.net>'

    def __init__(self, *args, instance, **kwargs) -> None:
        self.instance = instance

    @staticmethod
    def date_filter(date):
        return date_filter(date)

    @property
    def data(self):
        return (
            self.template_key_legacy,
            self.get_subject(),
            self.from_email,
            self.get_to_emails(),
            self.get_context_data(),
        )


class RegistrationReminderEmail(TemplateEmail):
    template_key_legacy = 'events.registrations.reminder'
    template = '_emails/events/registrations_reminder.md.html'
    from_email = 'HiPEAC <management@hipeac.net>'

    def get_subject(self) -> str:
        return f'[HiPEAC] Please update your registration for {self.instance.event.name}'

    def get_to_emails(self) -> List[str]:
        return [self.instance.user.email]

    def get_context_data(self):
        return {
            'user_name': self.instance.user.profile.name,
            'event_name': self.instance.event.name,
            'event_city': self.instance.event.city,
            'event_url': self.instance.event.get_absolute_url(),
            'registrations_count': self.instance.event.registrations_count,
            'registration_id': self.instance.id,
            'registration_url': self.instance.get_absolute_url(),
        }


class SessionReminderEmail(TemplateEmail):
    template_key_legacy = 'events.sessions.reminder'
    template = '_emails/events/sessions_reminder.md.html'
    from_email = 'HiPEAC <management@hipeac.net>'

    def get_subject(self) -> str:
        return f'[HiPEAC] Please update the information for "{self.instance.title}" session'

    def get_to_emails(self) -> List[str]:
        return [admin.user.email for admin in self.instance.acl.all()]

    def get_context_data(self):
        return {
            'event_name': self.instance.event.name,
            'event_city': self.instance.event.city,
            'event_url': self.instance.event.get_absolute_url(),
            'session_date': self.date_filter(self.instance.date),
            'session_title': self.instance.title,
            'session_type': self.instance.session_type.value,
            'session_editor_url': self.instance.get_editor_url(),
        }
