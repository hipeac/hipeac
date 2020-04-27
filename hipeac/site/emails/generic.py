from django.template.defaultfilters import date as date_filter


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
