import pytest

from django.core.exceptions import ValidationError

from hipeac.models.users import validate_membership_tags


class TestValidators:

    def test_membership_tags_invalid(self):
        with pytest.raises(ValidationError):
            validate_membership_tags('member,invalid')

    def test_membership_tags_incompatible1(self):
        with pytest.raises(ValidationError):
            validate_membership_tags('member,affiliated')

    def test_membership_tags_incompatible2(self):
        with pytest.raises(ValidationError):
            validate_membership_tags('nms,non-eu')
