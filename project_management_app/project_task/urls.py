from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect, name="home_redirect"),
    path("home/", views.home, name="home"),
    path("project-backlog/", views.project_backlog, name="project_backlog"),
    path('project-backlog/delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
]
