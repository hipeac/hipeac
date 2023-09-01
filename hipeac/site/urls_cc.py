from django.urls import path

import hipeac.site.views as views


urlpatterns = [
    path("", views.cc.HomeView.as_view(), name="homepage"),
    path("about/", views.cc.AboutView.as_view(), name="about"),
    path("projects/<int:pk>/<slug:slug>/", views.ProjectDetail.as_view(), name="project"),
]
