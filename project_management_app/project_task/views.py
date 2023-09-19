import json
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import DeleteView
from .models import Tag, Task
from .forms import CreateNewTaskForm
from django.db.models import Case, When, Value, IntegerField
import logging

# Set up logging
logger = logging.getLogger(__name__)


class TaskManager:
    """
    This class provides methods to manage tasks.
    """

    @staticmethod
    def create_task(cleaned_data):
        """
        This method creates a new task.
        """

        tags = cleaned_data.get('tags', [])  # Directly use 'get' for dictionaries
        tag_objects = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tags]

        task = CreateNewTaskForm(cleaned_data).save(commit=False)
        task.save()
        for tag in tag_objects:
            task.tags.add(tag)
        return True, f"Task '{str(task)}' successfully created!"

    @staticmethod
    def read_task(task_id):
        """
        This method reads a task.
        """
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return None

    @staticmethod
    def update_task(task_id, data):
        """
        This method updates a task.
        """
        task = TaskManager.read_task(task_id)
        if not task:
            return False, "Task not found"

        form = CreateNewTaskForm(data, instance=task)
        if form.is_valid():
            form.save()
            return True, f"Task '{str(task)}' successfully updated!"
        else:
            return False, form.errors

    @staticmethod
    def delete_task(task_id):
        """
        This method deletes a task.
        """
        task = TaskManager.read_task(task_id)
        if not task:
            return False, "Task not found"

        task.delete()
        return True, "Task successfully deleted!"

    @staticmethod
    def list_tasks(filter_criteria=None, sort_by=None):
        """
        List tasks based on some filtering criteria and sorting parameters.
        :param filter_criteria: A dictionary with model fields as keys.
        :param sort_by: A string representing the model field to sort by.
        :return: A queryset of matching tasks.
        """
        tasks = Task.objects.filter(**filter_criteria) if filter_criteria else Task.objects.all()

        if sort_by == "priority":
            tasks = tasks.annotate(
                custom_priority_order=Case(
                    When(priority="LOW", then=Value(0)),
                    When(priority="MED", then=Value(1)),
                    When(priority="IMP", then=Value(2)),
                    When(priority="URG", then=Value(3)),
                    default=Value(4),
                    output_field=IntegerField()
                )
            ).order_by("custom_priority_order")
        elif sort_by:
            tasks = tasks.order_by(sort_by)
        return tasks


class HomeView(View):
    """
    This class-based view renders the home page.
    """

    @staticmethod
    def get(request, *args, **kwargs):
        """
        This method renders the home page.
        """
        return render(request, "project_task/home.html", {"name": "home"})


class ProjectBacklogView(View):
    """
    This class-based view renders the project backlog page.
    """
    template_name = "project_task/project_backlog.html"

    def get(self, request, *args, **kwargs):
        form = CreateNewTaskForm()
        sort_by = request.GET.get('sort_by', 'priority')
        current_view = request.GET.get('view', 'list_view')  # Default to 'listView' if 'view' is not in the URL
        tasks = TaskManager.list_tasks(filter_criteria={"sprint": None}, sort_by=sort_by)
        return render(request, self.template_name, {
            "name": "project-backlog",
            "tasks": tasks,
            "form": form,
            "current_view": current_view,  # Pass the current view to the template
            "sort_by": sort_by  # Pass the sort_by parameter to the template
        })

    def post(self, *args, **kwargs):
        """
        This method handles the task creation.
        """
        form = CreateNewTaskForm(self.request.POST)
        if form.is_valid():
            success, message = TaskManager.create_task(form.cleaned_data)
            if success:
                tags_list = [str(tag) for tag in form.cleaned_data['tags']]
                return JsonResponse({'status': 'success', 'message': message, 'task': {**form.cleaned_data, 'tags': tags_list}})
            else:
                if isinstance(message, dict):  # If errors are returned as a dict
                    error_message = '; '.join([': '.join([key, val[0]]) for key, val in message.items()])
                else:
                    error_message = message
                return JsonResponse({'status': 'error', 'message': error_message})
        else:
            error_message = 'There were errors in your submission. Please correct them and try again.'
            logger.error(f"Form submission errors: {form.errors}")  # Log the errors for debugging
            return JsonResponse({'status': 'error', 'message': error_message})

    @staticmethod
    def form2json(data):
        """
        This method converts form data to JSON.
        """
        json_data = {}
        for key, value in data.items():
            if key == 'tags':
                json_data[key] = value.split(',')
            else:
                json_data[key] = value
        return json_data


class TaskDeleteView(DeleteView):
    """
    This class-based view deletes a task.
    """
    model = Task

    def get(self, request, *args, **kwargs):
        # TODO: Uncomment this section to enable backend check authenticated user for deletion
        """
        # A simple backend check to ensure user has the right to delete. Adjust as needed.
        if not request.user.has_perm('can_delete_task'):  # Assuming 'can_delete_task' is a permission
            return JsonResponse({
                'status': 'error',
                'message': "You don't have permission to delete this task."
            })
        """
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        This method deletes a task.
        """
        try:
            self.object = self.get_object()
            task_name = self.object.name  # Capture the task name for the feedback message
            self.object.delete()
            # Send success feedback
            return JsonResponse({
                'status': 'success',
                'message': f"Task '{task_name}' was successfully deleted!"
            })
        except Exception as e:
            # Handle any error during deletion and send error feedback
            return JsonResponse({
                'status': 'error',
                'message': f"Error deleting task: {str(e)}"
            })
