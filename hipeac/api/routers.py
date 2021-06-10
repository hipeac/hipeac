from rest_framework.routers import DefaultRouter

from hipeac.api import views


class Router(DefaultRouter):
    def __init__(self, version="v1"):
        super().__init__()

        self.schema_title = f"HiPEAC API {version}"

        self.register(r"awards/paper-awards", views.PaperAwardViewSet, basename="paper-award")
        self.register(
            r"awards/paper-awards/conferences", views.PublicationConferenceViewSet, basename="publication-conference"
        )
        self.register(r"awards/tech-transfer", views.TechTransferViewSet, basename="tech-transfer")
        self.register(r"events/b2b", views.B2bViewSet, basename="b2b")
        self.register(r"events/events", views.EventViewSet, basename="event")
        self.register(r"events/courses", views.CourseViewSet, basename="course")
        self.register(r"events/roadshows", views.RoadshowViewSet, basename="roadshow")
        self.register(r"events/sessions", views.SessionViewSet, basename="session")
        self.register(r"open-events", views.OpenEventViewSet, basename="open-event")
        self.register(r"open-registrations", views.OpenRegistrationViewSet, basename="open-registration")
        self.register(r"jobs", views.JobViewSet, basename="job")
        self.register(r"jobs/evaluations", views.JobEvaluationViewSet, basename="job-evaluation")
        self.register(r"communication/articles", views.ArticleViewSet, basename="article")
        self.register(r"communication/clippings", views.ClippingViewSet, basename="clipping")
        self.register(r"communication/quotes", views.QuoteViewSet, basename="quote")
        self.register(r"communication/magazines", views.MagazineViewSet, basename="magazine")
        self.register(r"communication/videos", views.VideoViewSet, basename="video")
        self.register(r"metadata", views.MetadataViewSet, basename="metadata")
        self.register(r"network/institutions", views.InstitutionViewSet, basename="institution")
        self.register(r"network/members", views.MemberViewSet, basename="member")
        self.register(r"network/partners", views.PartnerViewSet, basename="partner")
        self.register(r"network/projects", views.ProjectViewSet, basename="project")
        self.register(r"user", views.AuthUserViewSet, basename="auth-user")
        self.register(r"user/registrations", views.RegistrationViewSet, basename="auth-registration")
        self.register(r"users", views.UserViewSet, basename="user")
        self.register(r"vision", views.VisionViewSet, basename="vision")

        self.register(r"m/events/events", views.EventManagementViewSet, basename="event-management")

        self.register(r"steering/action-points", views.ActionPointViewSet, basename="sc-action-point")
        self.register(r"steering/meetings", views.MeetingViewSet, basename="sc-meeting")
        self.register(r"steering/membership-requests", views.MembershipRequestViewSet, basename="sc-membership-request")

    def get_urls(self):
        return [url for url in super().get_urls() if url.name != "auth-user-detail"]
