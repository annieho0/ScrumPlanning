from django.urls import path
from .views import HomeListView, TaskListView, TaskEditView, TaskDeleteView, SprintBoard, CreateGraphView


urlpatterns = [
    path("", HomeListView.as_view(), name="home_redirect"),
    path("home/", HomeListView.as_view(), name="home"),
    path("project-backlog/", TaskListView.as_view(), name="project_backlog"),
    path("project-backlog/edit_task/<int:task_id>/", TaskEditView.as_view(), name="edit_task"),
    path("project-backlog/delete_task/<int:task_id>/", TaskDeleteView.as_view(), name="delete_task"),
    # path("sprint-boards/get_updated_data/", SprintBoard.get_updated_data, name="get_updated_data"),
    path("sprint-boards/get_task_data/<int:task_id>/", SprintBoard.get_task_data, name="get_task_data"),
    path("sprint-boards/edit_task/<int:task_id>/", SprintBoard.edit_task, name="edit_task"),
    path('sprint_boards/<int:sprint_id>/', SprintBoard.sprint_boards, name='sprint_boards'),
    # path('redirect_to_sprint_board/<int:sprint_id>/', SprintBoard.redirect_to_sprint_board, name='redirect_to_sprint_board'),
    
    path('sprint_backlog/', SprintBoard.active_sprints, name='sprint_backlog'),
    path('sprint_backlog_archived', SprintBoard.archived_sprints, name='sprint_backlog_archived'),
    path('sprint_backlog/archive_sprint_backlog/<int:sprint_id>/', SprintBoard.archive_sprint_backlog, name='archive_sprint_backlog'),

    path("create-graph/", CreateGraphView.as_view(), name="create_graph"),
    path('move_selected_tasks_to_sprint/', SprintBoard.move_selected_tasks, name='move_selected_tasks_to_sprint'),
    #path("get_sprint_tasks/", SprintBoard.get_sprint_tasks, name="get_task")
]

