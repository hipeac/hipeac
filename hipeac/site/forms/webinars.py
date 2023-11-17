from crispy_forms.helper import FormHelper
from django.conf import settings
from django_recaptcha.fields import ReCaptchaField

from hipeac.forms import WebinarProposalForm as BaseWebinarProposalForm


class WebinarProposalForm(BaseWebinarProposalForm):
    captcha = None if settings.DEBUG else ReCaptchaField()

    class Meta(BaseWebinarProposalForm.Meta):
        exclude = ("accepted",)
        labels = {
            "title": "Please provide your webinar title",
            "organizers": "Please list the webinar organizers and their affiliations",
            "summary": "Please provide an abstract of your webinar",
            "topics": "Please select the keywords which relate to this event (select all that apply)",
            "application_areas": "Please select which of the following broad application areas this "
            "technology could be used for (select all that apply)",
            "projects": "Is your webinar connected to one or more European Union-funded projects? "
            "If so, please indicate which ones",
            "duration": "Please indicate the expected duration of the webinar. We recommend a couple of hours max.",
            "session_format": "Please indicate the format of your event",
            "expected_attendees": "Please indicate the expected number of attendees at your webinar",
            "previous_editions": "Have their been previous editions of this webinar? "
            "Please provide the location and date if so",
            "other": "Please add any other information you feel is relevant for the organization of this event, "
            "like other resources required in addition to the Zoom webinar",
        }
        help_texts = {
            "session_format": "Presentations / Panel discussion / Demonstration / Other",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
