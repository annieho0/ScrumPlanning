from django.urls import path
from .views import HomeView, ProjectBacklogView, TaskDeleteView

urlpatterns = [
    path("", HomeView.as_view(), name="home_redirect"),
    path("home/", HomeView.as_view(), name="home"),
    path("project-backlog/", ProjectBacklogView.as_view(), name="project_backlog"),
    path('project-backlog/delete_task/<int:pk>/', TaskDeleteView.as_view(), name='delete_task'),
]
