from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect, name="Home"),
    path("home/", views.home, name="Home"),
    path("project-backlog/", views.project_backlog, name="Project Backlog"),
]
