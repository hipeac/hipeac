from django.conf.urls import include
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.flatpages.views import flatpage
from django.contrib.sitemaps import views as sitemap_views
from django.urls import re_path
from django.views.generic import TemplateView

import hipeac.site.views as views
from .sitemaps import EventSitemap, InstitutionSitemap, JobSitemap, ProjectSitemap, SessionSitemap


sitemaps = {
    'events': EventSitemap,
    'flatpages': FlatPageSitemap,
    'institutions': InstitutionSitemap,
    'jobs': JobSitemap,
    'projects': ProjectSitemap,
    'sessions': SessionSitemap,
}

auth_patterns = [
    # https://github.com/ubernostrum/django-registration/blob/master/registration/backends/hmac/urls.py
    re_path(r'^activate/complete/$', views.ActivationCompleteView.as_view(), name='registration_activation_complete'),
    re_path(r'^activate/(?P<activation_key>[-:\w]+)/$', views.ActivationView.as_view(), name='registration_activate'),
    re_path(r'^join/$', views.RegistrationView.as_view(), name='registration_register'),
    re_path(r'^register/complete/$', views.RegistrationCompleteView.as_view(), name='registration_complete'),
    # https://github.com/django/django/blob/master/django/contrib/auth/urls.py
    re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    re_path(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    re_path(r'^password/change/$', views.PasswordChangeView.as_view(), name='password_change'),
    re_path(r'^password/change/done/$', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    re_path(r'^password/reset/$', views.PasswordResetView.as_view(), name='password_reset'),
    re_path(r'^password/reset/sent/$', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$', views.PasswordResetConfirmView.as_view(),
            name='password_reset_confirm'),
    re_path(r'^reset/done/$', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

urlpatterns = [
    # Main sections
    re_path(r'^$', TemplateView.as_view(template_name='flatpages/homepage.html'), name='homepage'),
    re_path(r'^jobs/$', TemplateView.as_view(template_name='recruitment/jobs.html'), name='jobs'),
    re_path(r'^jobs/feed/$', views.JobsFeed(), name='jobs_feed'),
    re_path(r'^jobs/(?P<pk>\d+).pdf$', views.JobsPdf.as_view(), name='jobs_pdf'),
    re_path(r'^jobs/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.JobDetail.as_view(), name='job'),
    re_path(r'^network/$', TemplateView.as_view(template_name='network/network.html'), name='network'),
    re_path(r'^network/institutions/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$',
            views.InstitutionDetail.as_view(), name='institution'),
    re_path(r'^network/projects/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.ProjectDetail.as_view(), name='project'),
    re_path(r'^news/$', TemplateView.as_view(template_name='news/news.html'), name='news'),
    re_path(r'^press/$', TemplateView.as_view(template_name='press/press.html'), name='press'),
    re_path(r'^vision/$', TemplateView.as_view(template_name='vision/vision.html'), name='vision'),
    # Events
    re_path(r'^events/$', TemplateView.as_view(template_name='events/events.html'), name='events'),
    re_path(r'^(?P<year>\d+)/(?P<slug>[\w-]+)/$', views.EventDetail.as_view(), name='conference'),
    re_path(r'^acaces/(?P<year>\d+)/(?P<slug>[\w-]+)/$', views.EventDetail.as_view(), name='acaces'),
    re_path(r'^csw/(?P<year>\d+)/(?P<slug>[\w-]+)/$', views.EventDetail.as_view(), name='csw'),
    re_path(r'^events/ec/(?P<pk>\d+)/$', views.EventDetail.as_view(), name='ec_meeting'),
    # Editor
    re_path(r'^editor/(?P<ct>\d+)/(?P<pk>\d+)/$', views.EditorView.as_view(), name='editor'),
    # Users
    re_path(r'^', include(auth_patterns)),
    re_path(r'^~(?P<username>[\w.@-]+)/$', views.JobDetail.as_view(), name='user'),
    # Sitemap
    re_path(r'^sitemap\.xml$', sitemap_views.index, {'sitemaps': sitemaps}),
    re_path(r'^sitemap-(?P<section>.+)\.xml$', sitemap_views.sitemap, {'sitemaps': sitemaps},
            name='django.contrib.sitemaps.views.sitemap'),
    # Flatpages “catchall” pattern
    re_path(r'^(?P<url>.*/)$', flatpage),
]
