from typing import List

from ..generic import TemplateEmail as OldTemplateEmail


class SessionProposalEmail(OldTemplateEmail):
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
