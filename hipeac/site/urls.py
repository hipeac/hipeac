from django.conf.urls import include
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.flatpages.views import flatpage
from django.contrib.sitemaps import views as sitemap_views
from django.urls import path, re_path
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

import hipeac.site.views as views

from .sitemaps import EventSitemap, InstitutionSitemap, JobSitemap, ProjectSitemap, SessionSitemap


sitemaps = {
    "events": EventSitemap,
    "flatpages": FlatPageSitemap,
    "institutions": InstitutionSitemap,
    "jobs": JobSitemap,
    "projects": ProjectSitemap,
    "sessions": SessionSitemap,
}

payment_patterns = (
    [
        path(
            "<int:pk>/",
            include(
                [
                    path("payment/", never_cache(views.RegistrationPaymentView.as_view()), name="payment"),
                    path(
                        "payment/result/",
                        never_cache(views.RegistrationPaymentResultView.as_view()),
                        name="payment_result",
                    ),
                    path("receipt.pdf", never_cache(views.RegistrationReceiptPdfView.as_view()), name="receipt"),
                    path(
                        "invoice-request/",
                        never_cache(views.RegistrationInvoiceRequestView.as_view()),
                        name="invoice_request",
                    ),
                ]
            ),
        ),
        path(
            "<uuid:uuid>/d/p/<slug:secret>/",
            include(
                [
                    path("", never_cache(views.RegistrationPaymentDelegatedView.as_view()), name="payment_delegated"),
                    path(
                        "result/",
                        never_cache(views.RegistrationPaymentDelegatedResultView.as_view()),
                        name="payment_delegated_result",
                    ),
                ]
            ),
        ),
    ],
    "payment_patterns",
)

urlpatterns = [
    path("", views.HomeView.as_view(), name="homepage"),
    # Recruitment
    path("jobs/euraxess.xml", views.JobsEuraxessXML.as_view(), name="jobs_euraxess_xml"),
    path("jobs1/", flatpage, {"url": "/jobs/"}, name="jobs__old"),
    path("jobs/", views.JobsView.as_view(), name="jobs"),
    path("jobs/feed/", views.JobsFeed(), name="jobs_feed"),
    path("jobs/management/", views.JobManagementView.as_view(), name="jobs_management"),
    path("jobs/<int:pk>.pdf", views.JobsPdf.as_view(), name="job_pdf"),
    path("jobfairs/<slug:code>/", views.JobFairView.as_view(), name="jobfair"),
    path("e/<int:job_id>/<int:value>/", views.JobEvaluationRedirect.as_view(), name="job_evaluation"),
    path("j<int:pk>", views.JobRedirect.as_view(), name="job_redirect"),
    re_path(r"^jobs/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$", views.JobDetail.as_view(), name="job"),
    # Network
    path("network/", flatpage, {"url": "/network/"}, name="network"),
    re_path(
        r"^network/institutions/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$",
        views.InstitutionDetail.as_view(),
        name="institution",
    ),
    re_path(r"^network/projects/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$", views.ProjectDetail.as_view(), name="project"),
    # Awards
    path("awards/", flatpage, {"url": "/awards/"}, name="awards"),
    path("awards/tech-transfer/create/", views.TechTransferApplicationCreateView.as_view(), name="techtransfer_create"),
    path(
        "awards/tech-transfer/update/<int:pk>/",
        views.TechTransferApplicationUpdateView.as_view(),
        name="techtransfer_update",
    ),
    # Communication
    path("news/", flatpage, {"url": "/news/"}, name="news"),
    path("news/feed/", views.NewsFeed(), name="news_feed"),
    re_path(r"^news/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$", views.ArticleDetail.as_view(), name="article"),
    path("press/", flatpage, {"url": "/press/"}, name="press"),
    path("magazine/<int:pk>/", views.MagazineDownload.as_view(), name="magazine_download_old"),
    path("magazine/<int:pk>.pdf", views.MagazineDownload.as_view(), name="magazine_download"),
    path("vision/", views.VisionDetail.as_view(), name="vision"),
    path("vision/<int:year>/", views.VisionDownload.as_view(), name="vision_download_old"),
    path("vision/<int:year>.pdf", views.VisionDownload.as_view(), name="vision_download"),
    path("vision/<int:year>/<int:id>.pdf", views.VisionArticleDownload.as_view(), name="vision_article_download"),
    # Events
    path("events/", flatpage, {"url": "/events/"}, name="events"),
    path("s/<int:pk>/", never_cache(views.SessionProposalCreate.as_view()), name="session_proposals"),
    path("s/<int:pk>/<uuid:slug>/", never_cache(views.SessionProposalUpdate.as_view()), name="session_proposal_update"),
    path("<int:year>/<slug:slug>/b2b/", views.EventB2BDetail.as_view(), name="conference_b2b"),
    path("<int:year>/<slug:slug>/stats/", views.EventStats.as_view(), name="conference_stats"),
    path("v1/<int:year>/<slug:slug>/", views.EventDetail.as_view(), name="conference_old"),
    path("<int:year>/<slug:slug>/", views.ConferenceDetail.as_view(), name="conference"),
    path("acaces/<int:year>/", views.AcacesDetail.as_view(), name="acaces"),
    path("acaces/<int:year>/management/", views.AcacesManagement.as_view(), name="acaces_management"),
    path("acaces/<int:year>/reports/<slug:report>.xlsx", views.AcacesReportSheet.as_view(), name="acaces_reports"),
    path("acaces/<int:year>/stats/", views.AcacesStats.as_view(), name="acaces_stats"),
    path("acaces/<int:year>/survey/", views.AcacesSurvey.as_view(), name="acaces_survey"),
    path("acaces/<int:year>/survey/gelato/", views.AcacesSurveyGelato.as_view(), name="acaces_gelato"),
    path("csw/<int:year>/<slug:slug>/", views.CswDetail.as_view(), name="csw"),
    path("events/ec/<int:pk>/", views.EventDetail.as_view(), name="ec_meeting"),
    path("webinars/", views.WebinarsView.as_view(), name="webinars"),
    path("webinar-proposal/", never_cache(views.WebinarProposalCreate.as_view()), name="webinar_proposals"),
    path("w/<uuid:slug>/", never_cache(views.WebinarProposalUpdate.as_view()), name="webinar_proposal_update"),
    re_path(r"^events/roadshow/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$", views.RoadshowDetail.as_view(), name="roadshow"),
    # payments
    path("registration/", include(payment_patterns, namespace="registration_payment")),
    path("done/", TemplateView.as_view(template_name="__v3__/pages/done.html"), name="done"),
    # Editor
    path("editor/new/<slug:model>/", never_cache(views.EditorCreateView.as_view()), name="editor_create"),
    path("editor/<int:ct>/<int:pk>/", never_cache(views.EditorView.as_view()), name="editor"),
    # Users
    re_path(r"^~(?P<slug>[\w.@+-]+)/$", views.UserProfile.as_view(), name="user"),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", views.UserSettings.as_view(), name="user_profile"),
    path("accounts/profileold/", views.UserSettingsOld.as_view(), name="user_profile_old"),
    path("accounts/certificates/", views.UserCertificates.as_view(), name="user_certificates"),
    path("accounts/certificates/<uuid:uuid>.pdf", views.UserCertificatePdf.as_view(), name="user_certificate_pdf"),
    # SC
    path("sc/", views.SteeringCommittee.as_view(), name="steering"),
    path("sc2/", views.SteeringCommitteeVue.as_view(), name="steering_vue"),
    # Mailing lists
    path("sympa/<slug:mailing_list>/", views.DataSourceView.as_view(), name="datasource"),
    # Media
    re_path(r"media/private(?P<path>((/\w+?)+/))(?P<filename>[\w.-]+)", views.PrivateFileView.as_view()),
    # Old redirects and legacy links
    path("mobility/collaboration/awardees/", views.CollaborationAwardees.as_view(), name="collaboration_awardees"),
    path("mobility/internships/awardees/", views.InternshipAwardees.as_view(), name="internship_awardees"),
    re_path(r"^press/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$", views.ArticleRedirect.as_view()),
    # Sitemap
    path("sitemap.xml", sitemap_views.index, {"sitemaps": sitemaps}),
    path(
        "sitemap-<slug:section>.xml",
        sitemap_views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
