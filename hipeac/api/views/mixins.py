from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser

from hipeac.models import File


class FilesMixin:
    @action(
        detail=True,
        methods=["post"],
        pagination_class=None,
        parser_classes=[FileUploadParser],
    )
    @method_decorator(never_cache)
    def files(self, request, *args, **kwargs):
        obj = self.get_object()

        # for users, we link the file to the profile
        if obj._meta.model_name == "user":
            obj = obj.profile

        file_keywords = [request.query_params.get("keyword", "")]
        file_type = request.query_params.get("type", File.PRIVATE)
        file_type = file_type if file_type in [File.PUBLIC, File.PRIVATE] else File.PRIVATE
        file = File(content_object=obj, type=file_type, keywords=file_keywords, file=request.data["file"])
        file.save()
        return self.retrieve(request, *args, **kwargs)
