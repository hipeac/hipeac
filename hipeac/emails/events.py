from hipeac.models.events import Registration, Session
from hipeac.services.mailer import TemplateEmail


class RegistrationEmail(TemplateEmail):
    def __init__(self, email_code: str, instance: Registration) -> None:
        super().__init__(email_code, to=[instance.user.email], instance=instance)


class SessionEmail(TemplateEmail):
    def __init__(self, email_code: str, instance: Session) -> None:
        admin_emails = [admin.user.email for admin in self.instance.acl.all()]
        super().__init__(email_code, to=admin_emails, instance=instance)
