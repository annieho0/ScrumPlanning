from django.urls import path
from .views import HomeListView, TaskListView, TaskEditView, TaskDeleteView, SprintBoard,CreateGraphView

urlpatterns = [
    path("", HomeListView.as_view(), name="home_redirect"),
    path("home/", HomeListView.as_view(), name="home"),
    path("project-backlog/", TaskListView.as_view(), name="project_backlog"),
    path("project-backlog/edit_task/<int:task_id>/", TaskEditView.as_view(), name="edit_task"),
    path("project-backlog/delete_task/<int:task_id>/", TaskDeleteView.as_view(), name="delete_task"),
    path("sprint-board/", SprintBoard.sprint_board, name="sprint_board"),
    path("sprint-backlog/", SprintBoard.sprint_backlog, name="sprint_backlog"),
    path("create-graph/",CreateGraphView.as_view() , name="create_graph"),
]
