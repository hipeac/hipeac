from celery.decorators import task
from typing import List

from hipeac.tools.emails import TemplateEmail


@task()
def send_from_template(template: str, subject: str, from_email: str, to: List[str], context_data: dict = {}):
    email = TemplateEmail(template=template, subject=subject, from_email=from_email, to=to, context_data=context_data)
    email.send()
