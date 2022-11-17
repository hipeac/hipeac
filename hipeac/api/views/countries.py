from django_countries import countries
from rest_framework.decorators import api_view, permission_classes, schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
@schema(None)
def get_countries(request, format=None):
    """
    Return a list of all countries.
    """
    return Response(dict(countries))
