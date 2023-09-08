from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect, name="home"),
    path("home/", views.home, name="home"),
    path("project-backlog/", views.project_backlog, name="project_backlog"),
]
