from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Tag, Task, Sprint
from .forms import CreateNewTaskForm


# Create your views here.
def home(response):
    """This view renders the home page"""
    form = CreateNewTaskForm()
    create_new_task(response)
    return render(response, "project_task/home.html", {"name": "home", "form": form})


def home_redirect(response):
    """This view redirects the user to the home page when they visit the root URL"""
    return home(response)


def project_backlog(response):
    """This view renders the project backlog page"""
    tasks = Task.objects.all().filter(sprint=None)
    statuses = [('NOT', 'Incomplete'), ('IN_PROG', 'In Progress'), ('COM', 'Complete')]
    return render(response, "project_task/project_backlog.html", {"name": "project-backlog", "tasks": tasks, "statuses": statuses})


def create_new_task(response):
    """This view renders the create new task page"""
    if response.method == "POST":
        # check and add tags to DB before creating the forms
        tags = response.POST.getlist('tags')
        for tag in tags:
            Tag.objects.get_or_create(name=tag)

        form = CreateNewTaskForm(response.POST)
        if form.is_valid():
            # Get the task instance but don't save to DB yet
            task = form.save(commit=False)

            # Now save the task to DB
            task.save()
            form.save_m2m()
            print("----------------- Sucessfully saved task -----------------")
            return redirect(reverse('project_backlog'))
        else:
            print("Form is not valid:", form.errors)


def delete_task(response, task_id):
    """
    This view deletes a task from the database
    """
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect(reverse('project_backlog'))

# def sprint_board(response):
#     """This view renders the project backlog page"""
#     tasks = Task.objects.all().filter(sprint=None)
#     tags = Tag.objects.all().filter(task=None)
#     statuses = [('NOT', 'Incomplete'), ('IN_PROG', 'In Progress'), ('COM', 'Complete')]
#     return render(response, "project_task/sprint_board.html", {"name": "sprint-board", "tasks": tasks, "statuses": statuses, "tag": tags})

# def filter_tasks(request):
#     selected_view = request.GET.get('filter', '')

#     if selected_view == "":
#         tasks = Task.objects.all()
#     else:
#         tasks = Task.objects.filter(category=selected_view)

#     return render(request, 'project_task/sprint_board.html', {'tasks': tasks})

def sprint_board(request):
    """This view renders the project backlog page"""
    tasks = Task.objects.filter(sprint=None)
    # Fetch unique tags associated with tasks
    tags = Tag.objects.filter(task__isnull=False).distinct()
    statuses = [('NOT', 'Incomplete'), ('IN_PROG', 'In Progress'), ('COM', 'Complete')]
    return render(request, "project_task/sprint_board.html", {"name": "sprint-board", "tasks": tasks, "statuses": statuses, "tags": tags})

def archive_sprint(request, sprint_id):
    sprint = Sprint.objects.get(pk=sprint_id)
    sprint.is_completed = True
    sprint.save()
    return redirect('sprint_backlog')

def delete_incomplete_tasks(request, sprint_id):
    sprint = Sprint.objects.get(pk=sprint_id)
    incomplete_tasks = Task.objects.filter(sprint=sprint, is_completed=False)
    incomplete_tasks.delete()
    return redirect('sprint_backlog')

def sprint_backlog(request):
    active_sprints = Sprint.objects.filter(is_completed=False)
    return render(request, 'project_task/sprint_backlog.html', {'active_sprints': active_sprints})

