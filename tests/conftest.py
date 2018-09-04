import maya
import pytest

from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient


@pytest.fixture()
def api_client():
    """A Django REST framework test client instance."""
    return APIClient(enforce_csrf_checks=True)


@pytest.fixture()
def now():
    """A MayaDT instance."""
    return maya.now()
