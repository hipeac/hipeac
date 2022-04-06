from typing import List

from ..generic import TemplateEmail


class AcacesAdmittedEmail(TemplateEmail):
    template_key_legacy = "events.acaces.admitted"
    template = "_emails/events/acaces/admitted.md.html"
    from_email = "HiPEAC <acaces@hipeac.net>"

    def get_subject(self) -> str:
        return f"[ACACES] Poster abstracts deadline for {self.instance.event.name}"

    def get_to_emails(self) -> List[str]:
        return [self.instance.user.email]

    def get_context_data(self):
        return {
            "user_name": self.instance.user.profile.name,
            "event_name": self.instance.event.name,
            "event_city": self.instance.event.city,
            "event_fee": self.instance.event.acaces.fee,
            "event_fee_discount": self.instance.event.acaces.shared_room_discount,
            "event_grant_request_deadline": self.instance.event.acaces.grant_request_deadline,
            "event_is_open_for_grants": self.instance.event.acaces.is_open_for_grants(),
            "registration_id": self.instance.id,
            "registration_url": self.instance.get_absolute_url(),
        }


class AcacesPosterAbstractsReminderEmail(TemplateEmail):
    template_key_legacy = "events.acaces.poster_abstracts_reminder"
    template = "_emails/events/acaces_poster_abstracts_reminder.md.html"
    from_email = "HiPEAC <acaces@hipeac.net>"

    def get_subject(self) -> str:
        return f"[ACACES] Poster abstracts deadline for {self.instance.event.name}"

    def get_to_emails(self) -> List[str]:
        return [self.instance.user.email]

    def get_context_data(self):
        return {
            "user_name": self.instance.user.profile.name,
            "registrations_count": self.instance.event.registrations_count,
            "registration_id": self.instance.id,
            "registration_url": self.instance.get_absolute_url(),
        }
