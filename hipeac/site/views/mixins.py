from django.shortcuts import redirect


class SlugMixin:
    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            self.object = super().get_object(queryset)
        return self.object

    def dispatch(self, request, *args, **kwargs):
        if not kwargs.get("slug") == self.get_object().slug:
            return redirect(self.get_object().get_absolute_url())
        return super().dispatch(request, *args, **kwargs)
