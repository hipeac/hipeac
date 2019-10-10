from typing import List

from .generic import TemplateEmail


class TechTransferApplicationEmail(TemplateEmail):
    template_key_legacy = 'awards.tech_transfer_applications.created'
    template = '_emails/awards/tech_transfer_applications_created.md.html'
    from_email = 'HiPEAC <management@hipeac.net>'

    def get_subject(self) -> str:
        return f'[HiPEAC] Your Tech Transfer Award application'

    def get_to_emails(self) -> List[str]:
        return [self.instance.applicant.email]

    def get_context_data(self):
        return {
            'user_name': self.instance.applicant.profile.name,
            'application_title': self.instance.title,
            'application_url': self.instance.get_absolute_url(),
        }
