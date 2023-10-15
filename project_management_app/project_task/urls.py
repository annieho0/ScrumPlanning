from django.urls import path
from .views import HomeListView, TaskListView, TaskEditView, TaskDeleteView, SprintBoard, CreateGraphView


urlpatterns = [
    path("", HomeListView.as_view(), name="home_redirect"),
    path("home/", HomeListView.as_view(), name="home"),
    path("project-backlog/", TaskListView.as_view(), name="project_backlog"),
    path("project-backlog/edit_task/<int:task_id>/", TaskEditView.as_view(), name="edit_task"),
    path("project-backlog/delete_task/<int:task_id>/", TaskDeleteView.as_view(), name="delete_task"),
    # path("sprint-board/", SprintBoard.sprint_board, name="sprint_board"),
    # path("sprint-boards/update_task/<int:task_id>/", SprintBoard.update_task, name="update_task"),
    path("sprint-boards/edit_task/<int:task_id>/", SprintBoard.edit_task, name="edit_task"),
    path('sprint_boards/<int:sprint_id>/', SprintBoard.sprint_boards, name='sprint_boards'),
    # path('redirect_to_sprint_board/<int:sprint_id>/', SprintBoard.redirect_to_sprint_board, name='redirect_to_sprint_board'),
    
    path('sprint_backlog/', SprintBoard.active_sprints, name='sprint_backlog'),
    path('sprint_backlog_archived', SprintBoard.archived_sprints, name='sprint_backlog_archived'),
    path('sprint_backlog/archive_sprint_backlog/<int:sprint_id>/', SprintBoard.archive_sprint_backlog, name='archive_sprint_backlog'),

    path("create-graph/", CreateGraphView.as_view(), name="create_graph"),
]

