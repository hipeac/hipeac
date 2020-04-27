from django import forms

from hipeac.models import TechTransferApplication


class TechTransferApplicationForm(forms.ModelForm):
    class Meta:
        model = TechTransferApplication
        readonly_fields = ("call", "applicant")
        exclude = ("awarded", "team", "team_string", "awardee", "awarded_from", "awarded_to", "awarded_summary")
        widgets = {
            "call": forms.HiddenInput(),
            "applicant": forms.HiddenInput(),
        }
