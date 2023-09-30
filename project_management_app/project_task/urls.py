from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect, name="home_redirect"),
    path("home/", views.home, name="home"),
    path("project-backlog/", views.project_backlog, name="project_backlog"),
    path('project-backlog/delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path("sprint-board/", views.sprint_board, name="sprint_board"),
    path('sprint/<int:sprint_id>/archive/', views.archive_sprint, name='archive_sprint'),
    path('sprint/<int:sprint_id>/delete_incomplete_tasks/', views.delete_incomplete_tasks, name='delete_incomplete_tasks'),
    path('sprint-backlog/', views.sprint_backlog, name='sprint_backlog'),
]
