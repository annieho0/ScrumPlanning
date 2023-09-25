from django.urls import path
from .views import HomeListView, TaskListView, TaskEditView, TaskDeleteView

urlpatterns = [
    path("", HomeListView.as_view(), name="home_redirect"),
    path("home/", HomeListView.as_view(), name="home"),
    path("project-backlog/", TaskListView.as_view(), name="project_backlog"),
    path("project-backlog/edit_task/<int:task_id>/", TaskEditView.as_view(), name="edit_task"),
    path("project-backlog/delete_task/<int:task_id>/", TaskDeleteView.as_view(), name="delete_task"),

]

