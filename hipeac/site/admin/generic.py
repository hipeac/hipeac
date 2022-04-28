from django.contrib import messages
from django.contrib.admin import FieldListFilter

from hipeac.models.emails import Email


def clean_tuple(t: tuple, fields_to_remove: list) -> tuple:
    return tuple(filter(lambda x: x not in fields_to_remove, t))


def custom_titled_filter(title):
    # https://stackoverflow.com/questions/17392087/how-to-modify-django-admin-filters-title

    class Wrapper(FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


# email actions


def create_email_action(email: Email) -> callable:
    def send_email(modeladmin, request, queryset):
        for instance in queryset:
            instance.get_email_class()(email.code, instance).send()
        messages.info(request, "Emails are being sent.")

    send_email.short_description = email.action_name
    send_email.__name__ = f"email.{email.code}".replace(".", "_")

    return send_email


def include_email_actions(actions: dict, prefix: str) -> dict:
    for email in Email.objects.filter(code__startswith=prefix).order_by("position"):
        action = create_email_action(email)
        actions[action.__name__] = (action, action.__name__, action.short_description)

    return actions
