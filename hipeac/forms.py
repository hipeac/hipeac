from django.core.validators import validate_comma_separated_integer_list
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple

from hipeac.models import get_cached_metadata_queryset


class CommaSeparatedIntegerChoiceField(MultipleChoiceField):
    widget = CheckboxSelectMultiple
    metadata_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        metadata = get_cached_metadata_queryset()
        self.choices = [(m.id, m.value) for m in metadata if m.type == self.metadata_type]

    def prepare_value(self, value):
        return value.split(',') if isinstance(value, str) else value

    def to_python(self, value):
        return ','.join(value)

    def validate(self, value):
        if value == '':
            return
        validate_comma_separated_integer_list(value)


class ApplicationAreasChoiceField(CommaSeparatedIntegerChoiceField):
    metadata_type = 'application_area'


class JobPositionChoiceField(CommaSeparatedIntegerChoiceField):
    metadata_type = 'job_position'


class TopicsChoiceField(CommaSeparatedIntegerChoiceField):
    metadata_type = 'topic'
