from hipeac.models.events import WebinarProposal
from hipeac.services.mailer import TemplateEmail


class WebinarProposalEmail(TemplateEmail):
    def __init__(self, email_code: str, instance: WebinarProposal) -> None:
        super().__init__("events.webinars.proposal", to=[instance.email], instance=instance)
