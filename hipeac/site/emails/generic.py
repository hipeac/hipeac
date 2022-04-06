from django.template.defaultfilters import date as date_filter

from hipeac.functions import send_task


class TemplateEmail:
    template_key_legacy = None
    template = None
    from_email = "HiPEAC <management@hipeac.net>"

    def __init__(self, *args, instance, **kwargs) -> None:
        self.instance = instance

    @staticmethod
    def date_filter(date):
        return date_filter(date)

    @property
    def data(self):
        return (
            self.template_key_legacy,
            self.get_subject(),
            self.from_email,
            self.get_to_emails(),
            self.get_context_data(),
        )

    def send(self) -> None:
        send_task("hipeac.tasks.emails.send_from_template", self.data)

    """
    This method could be used in the future.
    In any case this class needs to be refactored for allowing email templates stored on the database.

    def send(self) -> None:
        if self.instance:
            send_template_email(*self.get_data(self.instance))

        if self.queryset:
            eta = datetime.now()
            for instance in self.queryset:
                send_template_email.schedule(self.get_data(instance), eta=eta)
                eta = eta + timedelta(seconds=25)
    """
