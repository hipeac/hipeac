from django.conf.urls import patterns, url

from .views import DataSourceView


urlpatterns = patterns(
    '',
    url(r'^95C2A12BDE1BC52F7A5A1E63B1E69011BB16923AABAFFE3FB13F94FB3498C4F6/(?P<mailing_list>[\w-]+)$',
        DataSourceView.as_view(), name='datasource'),
)
