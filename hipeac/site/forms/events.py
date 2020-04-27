from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from django.conf import settings

from hipeac.forms import SessionProposalForm as BaseSessionProposalForm


class SessionProposalForm(BaseSessionProposalForm):
    captcha = None if settings.DEBUG else ReCaptchaField()

    class Meta(BaseSessionProposalForm.Meta):
        exclude = ("accepted",)
        labels = {
            "title": "Please provide your workshop or tutorial title",
            "organizers": "Please list the workshop organizers and their affiliations. "
            "For tutorials, please also provide a list of presenters with their short biographies",
            "summary": "Please provide an abstract of your event",
            "topics": "Please select the keywords which relate to this event (select all that apply)",
            "application_areas": "Please select which of the following broad application areas this "
            "technology could be used for (select all that apply)",
            "projects": "Is your event connected to one or more European Union-funded projects? "
            "If so, please indicate which ones",
            "workshop_deadlines": "Workshops only: please provide preliminary deadlines",
            "tutorial_biblio": "Tutorials only: please provide a short bibliography",
            "duration": "Please indicate the expected duration of your event",
            "session_format": "Please indicate the format of your event (select all that apply)",
            "expected_attendees": "Please indicate the expected number of attendees at your event",
            "room_configuration": "Please let us know what room configuration you would like",
            "previous_editions": "Have their been previous editions of this event? "
            "Please provide the location and date if so",
            "other": "Please add any other information you feel is relevant for the organization of this event",
        }
        help_texts = {
            "duration": "Full day / Half day / Other",
            "session_format": "Invited keynote talk / Presentations / Panel discussion / Demonstration / Other",
            "room_configuration": "Classroom-style / Theatre-style / Other",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class ThematicSessionProposalForm(SessionProposalForm):
    class Meta(BaseSessionProposalForm.Meta):
        exclude = ("accepted", "workshop_deadlines", "tutorial_biblio", "session_format", "previous_editions")
        labels = {
            "title": "Please provide your Thematic Session title",
            "organizers": "Please list the organizers and their affiliations.",
            "summary": "Motivation and objectives",
            "topics": "Please select the keywords which relate to this event (select all that apply)",
            "application_areas": "Please select which of the following broad application areas this "
            "technology could be used for (select all that apply)",
            "projects": "Is your event connected to one or more European Union-funded projects? "
            "If so, please indicate which ones",
            "duration": "Please indicate the expected duration of your event",
            "expected_attendees": "Please indicate the expected number of attendees at your event",
            "room_configuration": "Please let us know what room configuration you would like",
            "other": "HiPEAC financial support",
        }
        help_texts = {
            "duration": "One slot (1.5hr) / Two slots (3hr) / Other",
            "room_configuration": "Classroom-style / Theatre-style / Other",
            "other": "The network has a small budget to partially cover travel expenses of a key participant "
            "and possibly the organizer of the thematic session.",
        }
