from typing import List

from ..generic import TemplateEmail


class OpenRegistrationCreatedEmail(TemplateEmail):
    template_key_legacy = "events.open_registrations.created"
    template = "_emails/events/open_registrations_created.md.html"
    from_email = "HiPEAC <management@hipeac.net>"

    def get_subject(self) -> str:
        return f"[HiPEAC] Your registration for {self.instance.event.name}"

    def get_to_emails(self) -> List[str]:
        return [self.instance.email]

    def get_context_data(self):
        return {
            "user_name": f"{self.instance.first_name} {self.instance.last_name}",
            "event_name": self.instance.event.name,
            "event_city": self.instance.event.city,
            "event_url": self.instance.event.custom_url,
            "registrations_count": self.instance.event.registrations_count,
            "registration_id": self.instance.uuid,
            "registration_url": self.instance.get_absolute_url(),
            "visa_requested": self.instance.visa_requested,
        }


class RegistrationReminderEmail(TemplateEmail):
    template_key_legacy = "events.registrations.reminder"
    template = "_emails/events/registrations_reminder.md.html"
    from_email = "HiPEAC <management@hipeac.net>"

    def get_subject(self) -> str:
        return f"[HiPEAC] Please update your registration for {self.instance.event.name}"

    def get_to_emails(self) -> List[str]:
        return [self.instance.user.email]

    def get_context_data(self):
        return {
            "is_virtual": self.instance.event.is_virtual,
            "user_name": self.instance.user.profile.name,
            "event_name": self.instance.event.name,
            "event_city": self.instance.event.city,
            "event_url": self.instance.event.get_absolute_url(),
            "registrations_count": self.instance.event.registrations_count,
            "registration_id": self.instance.id,
            "registration_url": self.instance.get_absolute_url(),
        }


class PaymentReminderEmail(RegistrationReminderEmail):
    template_key_legacy = "events.registrations.payment_reminder"
    template = "_emails/registrations_payment_reminder.md.html"

    def get_subject(self) -> str:
        return f"[{self.instance.event.hashtag}] Payment reminder / {self.instance.id}"


class SessionProceedingsEmail(TemplateEmail):
    template_key_legacy = "events.sessions.proceedings"
    template = "_emails/events/sessions_proceedings.md.html"
    from_email = "HiPEAC <webmaster@hipeac.net>"

    def get_subject(self) -> str:
        return f'[HiPEAC] Presentations from the "{self.instance.title}" session'

    def get_to_emails(self) -> List[str]:
        return [admin.user.email for admin in self.instance.acl.all()]

    def get_context_data(self):
        return {
            "event_name": self.instance.event.name,
            "event_city": self.instance.event.city,
            "event_url": self.instance.event.get_absolute_url(),
            "session_date": self.date_filter(self.instance.start_at.date()),
            "session_title": self.instance.title,
            "session_type": self.instance.type.value,
        }


class SessionReminderEmail(TemplateEmail):
    template_key_legacy = "events.sessions.reminder"
    template = "_emails/events/sessions_reminder.md.html"
    from_email = "HiPEAC <management@hipeac.net>"

    def get_subject(self) -> str:
        return f'[HiPEAC] Please update the information for "{self.instance.title}" session'

    def get_to_emails(self) -> List[str]:
        return [admin.user.email for admin in self.instance.acl.all()]

    def get_context_data(self):
        return {
            "event_name": self.instance.event.name,
            "event_city": self.instance.event.city,
            "event_url": self.instance.event.get_absolute_url(),
            "session_date": self.date_filter(self.instance.start_at.date()),
            "session_title": self.instance.title,
            "session_type": self.instance.type.value,
            "session_editor_url": self.instance.get_editor_url(),
        }


class SessionSpeakersReminderEmail(TemplateEmail):
    template_key_legacy = "events.sessions.speakers_reminder"
    template = "_emails/events/sessions_speakers_reminder.md.html"
    from_email = "HiPEAC <management@hipeac.net>"

    def get_subject(self) -> str:
        return f'[HiPEAC] Please check speakers for "{self.instance.title}" session'

    def get_to_emails(self) -> List[str]:
        return [admin.user.email for admin in self.instance.acl.all()]

    def get_context_data(self):
        return {
            "event_name": self.instance.event.name,
            "event_city": self.instance.event.city,
            "event_url": self.instance.event.get_absolute_url(),
            "session_date": self.date_filter(self.instance.start_at.date()),
            "session_title": self.instance.title,
            "session_type": self.instance.type.value,
        }


class NoShowsEmail(TemplateEmail):
    template_key_legacy = "events.no_shows"
    template = "_emails/events/no_shows.md.html"
    from_email = "HiPEAC <management@hipeac.net>"

    def get_subject(self) -> str:
        return f"[HiPEAC] Please confirm your attendance for {self.instance.event.name}"

    def get_to_emails(self) -> List[str]:
        return [self.instance.user.email]

    def get_context_data(self):
        return {
            "user_name": self.instance.user.profile.name,
            "event_name": self.instance.event.name,
            "event_city": self.instance.event.city,
            "event_url": self.instance.event.get_absolute_url(),
            "registrations_count": self.instance.event.registrations_count,
            "registration_id": self.instance.id,
            "registration_url": self.instance.get_absolute_url(),
        }


class SessionProposalEmail(TemplateEmail):
    template_key_legacy = "events.session_proposals.created"
    template = "_emails/events/session_proposals_created.md.html"
    from_email = "HiPEAC <management@hipeac.net>"

    def get_subject(self) -> str:
        return f'[HiPEAC] Your session proposal: "{self.instance.title}""'

    def get_to_emails(self) -> List[str]:
        from hipeac.models import Event

        email = {Event.CSW: "xavim@ac.upc.edu", Event.CONFERENCE: "workshops@hipeac.net"}[self.instance.event.type]
        return [self.instance.email, email]

    def get_context_data(self):
        return {
            "event_name": str(self.instance.event),
            "session_title": self.instance.title,
            "session_url": self.instance.get_absolute_url(),
            "user_name": f"{self.instance.first_name} {self.instance.last_name}",
        }
