from rest_framework.routers import DefaultRouter

from hipeac.api import views


class Router(DefaultRouter):
    def __init__(self, version='v1'):
        super().__init__()

        self.schema_title = f'HiPEAC API {version}'

        self.register(r'events/events', views.EventViewSet, base_name='event')
        self.register(r'events/roadshows', views.RoadshowViewSet, base_name='roadshow')
        self.register(r'events/sessions', views.SessionViewSet, base_name='session')
        self.register(r'jobs', views.JobViewSet, base_name='job')
        self.register(r'jobs/evaluations', views.JobEvaluationViewSet, base_name='job-evaluation')
        self.register(r'communication/clippings', views.ClippingViewSet, base_name='clipping')
        self.register(r'communication/quotes', views.QuoteViewSet, base_name='quote')
        self.register(r'communication/articles', views.ArticleViewSet, base_name='article')
        self.register(r'communication/videos', views.VideoViewSet, base_name='video')
        self.register(r'metadata', views.MetadataViewSet, base_name='metadata')
        self.register(r'network/institutions', views.InstitutionViewSet, base_name='institution')
        self.register(r'network/members', views.MemberViewSet, base_name='member')
        self.register(r'network/projects', views.ProjectViewSet, base_name='project')
        self.register(r'research/paper-awards', views.PaperAwardViewSet, base_name='paper-award')
        self.register(r'research/paper-awards/conferences', views.PublicationConferenceViewSet,
                      base_name='publication-conference')
        self.register(r'user', views.AuthUserViewSet, base_name='auth-user')
        self.register(r'user/registrations', views.RegistrationViewSet, base_name='auth-registration')
        self.register(r'users', views.UserViewSet, base_name='user')
        self.register(r'vision', views.VisionViewSet, base_name='vision')

    def get_urls(self):
        return [url for url in super().get_urls() if url.name != 'auth-user-detail']
