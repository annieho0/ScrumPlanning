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
    def list_tasks(filter_criteria=None, priority_sort_value=None, tag_filter_value=[]):
        """
        List tasks based on some filtering criteria and sorting parameters.
        :param filter_criteria: A dictionary with model fields as keys.
        :param priority_sort_value: A string representing the model field to sort by.
        :param tag_filter_value: A list of tag names to filter by.
        :return: A queryset of matching tasks.
        """
        tasks = Task.objects.filter(**filter_criteria) if filter_criteria else Task.objects.all()

        # Filter by tags
        if tag_filter_value:
            tasks = tasks.filter(tags__name__in=tag_filter_value).distinct()

        # Sort by priority
        if priority_sort_value == "priority_ascending":
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
        elif priority_sort_value == "priority_descending":
            tasks = tasks.annotate(
                custom_priority_order=Case(
                    When(priority="LOW", then=Value(3)),
                    When(priority="MED", then=Value(2)),
                    When(priority="IMP", then=Value(1)),
                    When(priority="URG", then=Value(0)),
                    default=Value(4),
                    output_field=IntegerField()
                )
            ).order_by("custom_priority_order")
        elif priority_sort_value:
            tasks = tasks.order_by(priority_sort_value)
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

        priority_sort = request.GET.get('priority_sort', 'priority_ascending')
        current_view = request.GET.get('view', 'list_view')

        # Filter Tags that is in use currently from the database
        used_tags_ids = Task.objects.values_list('tags', flat=True).distinct()
        tags = Tag.objects.filter(id__in=used_tags_ids)
        # Clean up the selected tags passed by the URL
        selected_tags_string = request.GET.get('tags_filter', '')
        selected_tags = selected_tags_string.split(",") if selected_tags_string else []

        print(selected_tags)
        tasks = TaskManager.list_tasks(filter_criteria={"sprint": None}, priority_sort_value=priority_sort,
                                       tag_filter_value=selected_tags)
        return render(request, self.template_name, {
            "name": "project-backlog",
            "tasks": tasks,
            "tags": tags,  # Pass the tags to the template
            "form": form,
            "current_view": current_view,  # Pass the current view to the template
            "priority_sort": priority_sort,  # Pass the sort_by parameter to the template
            "selected_tags": selected_tags  # Pass the selected tags to the template
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
                return JsonResponse(
                    {'status': 'success', 'message': message, 'task': {**form.cleaned_data, 'tags': tags_list}})
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
