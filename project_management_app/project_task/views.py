from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Tag, Task
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
