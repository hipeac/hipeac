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
    path('jobs/<int:pk>.pdf', views.JobsPdf.as_view(), name='jobs_pdf'),
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
    # Research
    path('research/', flatpage, {'url': '/research/'}, name='research'),
    # Events
    path('events/', flatpage, {'url': '/events/'}, name='events'),
    path('<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='conference'),
    path('acaces/<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='acaces'),
    path('csw/<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='csw'),
    path('events/ec/<int:pk>/', views.EventDetail.as_view(), name='ec_meeting'),
    re_path(r'^events/roadshow/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.RoadshowDetail.as_view(), name='roadshow'),
    # Editor
    path('editor/<int:ct>/<int:pk>/', never_cache(views.EditorView.as_view()), name='editor'),
    # Users
    re_path(r'^~(?P<username>[\w.@-]+)/$', views.JobDetail.as_view(), name='user'),
    path('accounts/', include('allauth.urls')),
    path('accounts/privacy/', views.PrivacySettings.as_view(), name='user_privacy'),
    path('accounts/profile/', views.ProfileSettings.as_view(), name='user_profile'),
    path('accounts/certificates/', views.JobDetail.as_view(), name='user_certificates'),
    path('accounts/research-group/', views.JobDetail.as_view(), name='user_research_group'),
    path('accounts/research/', views.JobDetail.as_view(), name='user_research'),
    # Mailing lists
    path('sympa/<slug:mailing_list>/', views.DataSourceView.as_view(), name='datasource'),
    # Sitemap
    path('sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps}),
    path('sitemap-<slug:section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]
