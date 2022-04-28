from anymail.message import AnymailMessage
from celery.execute import send_task
from django import template
from django.conf import settings
from django.db.models import Model
from typing import List, Optional

from hipeac.models.emails import Email


class TemplateEmail:
    def __init__(
        self,
        email_code: str,
        *,
        instance: Model,
        to: List[str],
        subject: Optional[str] = None,
    ) -> None:
        try:
            self.email = Email.objects.get(code=email_code)
        except Email.DoesNotExist:
            raise ValueError(f'"{email_code}" is not registered.')

        self.to = to
        self.subject = subject or self.email.subject.format(obj=instance)
        templ = template.Template(self.email.template)
        self.text_content = templ.render(template.Context({"email_format": "txt", "obj": instance}))
        self.html_content = templ.render(template.Context({"email_format": "html", "obj": instance}))

    def send(self) -> None:
        data = {
            "from_email": self.email.from_email,
            "to": self.to,
            "cc": self.email.cc_emails,
            "reply_to": [self.email.reply_to_email] if self.email.reply_to_email else None,
            "subject": self.subject,
            "body": self.text_content,
        }

        if settings.DEBUG:
            email = AnymailMessage(**data)
            email.attach_alternative(self.html_content, "text/html")
            email.send()
        else:
            send_task("hipeac.tasks.emails.send_template", ({**data, "html_content": self.html_content},))
