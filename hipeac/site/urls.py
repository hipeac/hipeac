from django.conf.urls import include
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.flatpages.views import flatpage
from django.contrib.sitemaps import views as sitemap_views
from django.urls import path, re_path
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

urlpatterns = [
    # Main sections
    path('', TemplateView.as_view(template_name='flatpages/homepage.html'), name='homepage'),
    path('jobs/', flatpage, {'url': '/jobs/'}, name='jobs'),
    path('jobs/feed/', views.JobsFeed(), name='jobs_feed'),
    path('jobs/<int:pk>.pdf', views.JobsPdf.as_view(), name='jobs_pdf'),
    re_path(r'^jobs/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.JobDetail.as_view(), name='job'),
    path('network/', flatpage, {'url': '/network/'}, name='network'),
    re_path(r'^network/institutions/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$',
            views.InstitutionDetail.as_view(), name='institution'),
    re_path(r'^network/projects/(?P<pk>\d+)(?:/(?P<slug>[\w-]+))?/$', views.ProjectDetail.as_view(), name='project'),
    path('news/', flatpage, {'url': '/news/'}, name='news'),
    path('press/', flatpage, {'url': '/press/'}, name='press'),
    path('vision/', flatpage, {'url': '/vision/'}, name='vision'),
    # Events
    path('events/', flatpage, {'url': '/events/'}, name='events'),
    path('<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='conference'),
    path('acaces/<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='acaces'),
    path('csw/<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='csw'),
    path('events/ec/<int:pk>/', views.EventDetail.as_view(), name='ec_meeting'),
    # Editor
    path('editor/<int:ct>/<int:pk>/', views.EditorView.as_view(), name='editor'),
    # Users
    re_path(r'^~(?P<username>[\w.@-]+)/$', views.JobDetail.as_view(), name='user'),
    # Mailing lists
    path('sympa/<slug:mailing_list>/', views.DataSourceView.as_view(), name='datasource'),
    # Sitemap
    path('sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps}),
    path('sitemap-<slug:section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]
