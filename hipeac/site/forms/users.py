from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from django_countries.fields import CountryField

from hipeac.models import Profile


class UserPrivacyForm(forms.ModelForm):
    is_public = forms.TypedChoiceField(
        label="Do you like this website?",
        choices=((1, "Yes"), (0, "No")),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )

    class Meta(object):
        model = Profile
        fields = ('is_public', 'is_subscribed')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Privacy settings',
                'is_public',
                'is_subscribed',
            ),
            ButtonHolder(
                Submit('submit', 'Update', css_class='btn btn-primary mt-3')
            )
        )


class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(required=True)
    country = CountryField().formfield()

    class Meta(object):
        model = Profile
        fields = (
            'country', 'bio',
            'institution', 'department', 'position', 'second_institution',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Personal information',
                'country',
                'bio',
            ),
            Fieldset(
                'Affiliation',
                'institution',
                'department',
                'position',
                'second_institution',
            ),
            ButtonHolder(
                Submit('submit', 'Update', css_class='btn btn-primary mt-3')
            )
        )
