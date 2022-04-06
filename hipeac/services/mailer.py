from anymail.message import AnymailMessage
from django import template
from typing import List, Optional

from hipeac.models.emails import Email


class TemplateEmail:
    def __init__(
        self, *, email_code: str, to: List[str], context_data: dict = {}, subject: Optional[str] = None
    ) -> None:
        try:
            email = Email.objects.get(code=email_code)
        except Email.DoesNotExist:
            raise ValueError(f'"{email_code}" is not registered.')

        subject = subject or email.subject
        tem = template.Template(email.template)
        text_content = tem.render(template.Context({**{"email_format": "txt"}, **context_data}))
        html_content = tem.render(template.Context({**{"email_format": "html"}, **context_data}))

        to.append(email.extra_to_emails)
        self.message = AnymailMessage(subject=subject, from_email=email.from_email, to=to, body=text_content)
        self.message.attach_alternative(html_content, "text/html")

    def send(self):
        self.message.send()
