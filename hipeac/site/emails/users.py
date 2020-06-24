from typing import List

from .generic import TemplateEmail


class UserContactEmail(TemplateEmail):
    template_key_legacy = "users.contact"
    template = "_emails/users/contact.md.html"
    from_email = "HiPEAC <noreply@hipeac.net>"

    def get_subject(self) -> str:
        return "You have received a message via HiPEAC"

    def get_to_emails(self) -> List[str]:
        return [self.instance["user"].email]

    def get_context_data(self):
        return {
            "user_name": self.instance["user"].profile.name,
            "sender_first_name": self.instance["sender"].first_name,
            "sender_name": self.instance["sender"].profile.name,
            "sender_affiliation": self.instance["sender"].profile.institution.name
            if self.instance["sender"].profile.institution
            else None,
            "sender_email": self.instance["sender"].email,
            "message": self.instance["message"],
        }
