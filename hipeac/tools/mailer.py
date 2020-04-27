from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_internal_email(*, to: str, subject: str, template: str, context):
    from_email = "HiPEAC <noreply@hipeac.net>"
    text_content = render_to_string(template, context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.send()
