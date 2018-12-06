from allauth.account.forms import SignupForm
from captcha.fields import ReCaptchaField
from django import forms
from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

from hipeac.models import get_cached_metadata_queryset, validate_membership_tags


class HiSignupForm(SignupForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.DEBUG:
            self.fields['captcha'] = ReCaptchaField(attrs={'theme': 'clean'})


class CommaSeparatedChoiceField(MultipleChoiceField):
    widget = CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            self.choices = self._get_custom_choices()
        except Exception:
            self.choices = ()

    def prepare_value(self, value):
        return value.split(',') if isinstance(value, str) else value

    def to_python(self, value):
        return ','.join(value)


class MembershipTagsChoiceField(CommaSeparatedChoiceField):

    def _get_custom_choices(self):
        return (
            ('---', (
                ('member', 'Member'),
                ('affiliated', 'Affiliated Member'),
            )),
            ('--- Geographic attributes', (
                ('non-eu', 'Outside Europe (associated)'),
                ('nms', 'New member state (NMS)'),
            )),
            ('--- Other attributes', (
                ('innovation', 'Innovation member'),
                ('industry', 'Industry member'),
                ('phd', 'PhD student'),
                ('staff', 'Staff member'),
            )),
        )

    def validate(self, value):
        if value == '':
            return
        validate_membership_tags(value)


class MetadataChoiceField(CommaSeparatedChoiceField):
    metadata_type = None

    def _get_custom_choices(self):
        """Choices are only set when a database exists."""
        metadata = get_cached_metadata_queryset()
        return [(m.id, m.value) for m in metadata if m.type == self.metadata_type]

    def validate(self, value):
        if value == '':
            return
        validate_comma_separated_integer_list(value)


class ApplicationAreasChoiceField(MetadataChoiceField):
    metadata_type = 'application_area'


class JobPositionChoiceField(MetadataChoiceField):
    metadata_type = 'job_position'


class TopicsChoiceField(MetadataChoiceField):
    metadata_type = 'topic'
