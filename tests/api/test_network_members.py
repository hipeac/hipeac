import pytest

from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestForAnonymous:
    list_url = reverse('v1:member-list')

    def test_list(self, api_client, db):
        assert api_client.get(self.list_url).status_code == status.HTTP_200_OK

    def test_create(self, api_client):
        assert api_client.post(self.list_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.skip(reason='HTTP_405_METHOD_NOT_ALLOWED')
    def test_read(self, api_client):
        pass

    @pytest.mark.skip(reason='HTTP_405_METHOD_NOT_ALLOWED')
    def test_update(self, api_client):
        pass

    @pytest.mark.skip(reason='HTTP_405_METHOD_NOT_ALLOWED')
    def test_delete(self, api_client):
        pass
