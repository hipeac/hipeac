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

        # new
        self.register(r"events/acaces", views.AcacesViewSet, basename="acaces")
        self.register(r"events/acaces/courses", views.AcacesCourseViewSet, basename="course")
        self.register(r"events/acaces/management", views.AcacesManagementViewSet, basename="acaces-management")
        self.register(
            r"events/acaces/management/grant", views.AcacesGrantManagementViewSet, basename="acaces-grant-management"
        )
        self.register(
            r"events/acaces/management/registration",
            views.AcacesRegistrationManagementViewSet,
            basename="acaces-registration-management",
        )
        self.register(r"events/conferences", views.ConferenceViewSet, basename="conference")
        self.register(r"events/csw", views.CswViewSet, basename="csw")

        self.register(
            r"user/registrations/acaces", views.AcacesRegistrationViewSet, basename="auth-registration-acaces"
        )
        self.register(
            r"user/registrations/conferences",
            views.ConferenceRegistrationViewSet,
            basename="auth-registration-conference",
        )
        self.register(r"user/registrations/csw", views.CswRegistrationViewSet, basename="auth-registration-csw")

        # job fairs
        self.register("jobfairs", views.JobFairViewSet, basename="jobfair")
        self.register(
            "user/registrations/fairs", views.JobFairRegistrationViewSet, basename="auth-registration-jobfair"
        )

        self.register(r"events/events", views.EventViewSet, basename="event")
        self.register(r"events/roadshows", views.RoadshowViewSet, basename="roadshow")
        self.register(r"events/sessions", views.SessionViewSet, basename="session")
        self.register(r"files", views.FileViewSet, basename="file")
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
        self.register(r"user/registrations", views.RegistrationViewSet, basename="auth-registration")  # TODO: remove
        self.register(r"user/webinars", views.RegistrationViewSet, basename="auth-webinar")
        self.register(r"users", views.UserViewSet, basename="user")
        self.register(r"vision", views.VisionViewSet, basename="vision")
        self.register(r"webinars", views.WebinarViewSet, basename="webinar")

        self.register(r"m/events/events", views.EventManagementViewSet, basename="event-management")

        self.register(r"steering/action-points", views.ActionPointViewSet, basename="sc-action-point")
        self.register(r"steering/meetings", views.MeetingViewSet, basename="sc-meeting")
        self.register(r"steering/membership-requests", views.MembershipRequestViewSet, basename="sc-membership-request")

    def get_urls(self):
        return [url for url in super().get_urls() if url.name != "auth-user-detail"]
