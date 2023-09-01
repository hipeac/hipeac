from hipeac.api.serializers.cc import CCSerializer
from hipeac.models.cc import CC

from ..inertia import InertiaView


class HomeView(InertiaView):
    vue_entry_point = "apps/cc/home/main.ts"

    def get_props(self, request, *args, **kwargs) -> dict:
        return {
            "projects": CCSerializer(
                CC.objects.select_related("project"), many=True, context={"request": request}
            ).data,
        }


class AboutView(HomeView):
    vue_entry_point = "apps/cc/about/main.ts"
