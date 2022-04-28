from typing import List

from ..generic import TemplateEmail as OldTemplateEmail


class AcacesPosterAbstractsReminderEmail(OldTemplateEmail):
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
