from django.conf.urls import include
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.flatpages.views import flatpage
from django.contrib.sitemaps import views as sitemap_views
from django.urls import path, re_path
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

import hipeac.site.views as views
from .sitemaps import EventSitemap, InstitutionSitemap, JobSitemap, ProjectSitemap, RoadshowSitemap, SessionSitemap


sitemaps = {
    'events': EventSitemap,
    'flatpages': FlatPageSitemap,
    'institutions': InstitutionSitemap,
    'jobs': JobSitemap,
    'projects': ProjectSitemap,
    'roadshows': RoadshowSitemap,
    'sessions': SessionSitemap,
}

urlpatterns = [
    # Recruitment
    path('', TemplateView.as_view(template_name='flatpages/homepage.html'), name='homepage'),
    path('jobs/', flatpage, {'url': '/jobs/'}, name='jobs'),
    path('jobs/feed/', views.JobsFeed(), name='jobs_feed'),
    path('jobs/management/', flatpage, {'url': '/jobs/'}, name='jobs_management'),
    path('jobs/<int:pk>.pdf', views.JobsPdf.as_view(), name='job_pdf'),
    path('e/<int:job_id>/<int:value>/', views.JobEvaluationRedirect.as_view(), name='job_evaluation'),
    path('j<int:pk>', views.JobRedirect.as_view(), name='job_redirect'),
    re_path(r'^jobs/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.JobDetail.as_view(), name='job'),
    # Network
    path('network/', flatpage, {'url': '/network/'}, name='network'),
    re_path(r'^network/institutions/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$',
            views.InstitutionDetail.as_view(), name='institution'),
    re_path(r'^network/projects/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.ProjectDetail.as_view(), name='project'),
    # Communication
    path('news/', flatpage, {'url': '/news/'}, name='news'),
    path('news/feed/', views.NewsFeed(), name='news_feed'),
    re_path(r'^news/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.ArticleDetail.as_view(), name='article'),
    path('press/', flatpage, {'url': '/press/'}, name='press'),
    path('vision/', flatpage, {'url': '/vision/'}, name='vision'),
    path('vision/<int:year>/', views.VisionDownload.as_view(), name='vision_download'),
    # Research
    path('research/', flatpage, {'url': '/research/'}, name='research'),
    # Events
    path('events/', flatpage, {'url': '/events/'}, name='events'),
    path('<int:year>/<slug:slug>/stats/', views.EventStats.as_view(), name='conference_stats'),
    path('<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='conference'),
    path('acaces/<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='acaces'),
    path('csw/<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='csw'),
    path('events/ec/<int:pk>/', views.EventDetail.as_view(), name='ec_meeting'),
    re_path(r'^events/roadshow/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.RoadshowDetail.as_view(), name='roadshow'),
    path('registration/payment/<int:pk>/result/', never_cache(views.RegistrationPaymentResultView.as_view()),
         name='registration_payment_result'),
    path('registration/payment/<int:pk>/', never_cache(views.RegistrationPaymentView.as_view()),
         name='registration_payment'),
    path('registration/receipt/<int:pk>/', views.RegistrationReceiptPdfView.as_view(), name='registration_receipt'),
    # Editor
    path('editor/new/<slug:model>/', never_cache(views.EditorCreateView.as_view()), name='editor_create'),
    path('editor/<int:ct>/<int:pk>/', never_cache(views.EditorView.as_view()), name='editor'),
    # Users
    re_path(r'^~(?P<slug>[\w.@-]+)/$', views.UserProfile.as_view(), name='user'),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.UserSettings.as_view(), name='user_profile'),
    path('accounts/certificates/', views.UserCertificates.as_view(), name='user_certificates'),
    path('accounts/certificates/<uuid:uuid>.pdf', views.UserCertificatePdf.as_view(), name='user_certificate_pdf'),
    # Mailing lists
    path('sympa/<slug:mailing_list>/', views.DataSourceView.as_view(), name='datasource'),
    # Media
    re_path(r'media/private(?P<path>((/\w+?)+/))(?P<filename>[\w.-]+)', views.FirewallView.as_view()),
    # Old redirects
    re_path(r'^press/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.ArticleRedirect.as_view()),
    # Sitemap
    path('sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps}),
    path('sitemap-<slug:section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]
