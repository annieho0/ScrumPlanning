import json
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import DeleteView, UpdateView, CreateView
from .models import Tag, Task
from .forms import CreateNewTaskForm, EditTaskForm
from django.db.models import Case, When, Value, IntegerField
import logging

# Set up logging
logger = logging.getLogger(__name__)


class TaskManager:
    """
    This class provides methods to manage tasks.
    """

    @staticmethod
    def create_task(data):
        """
        This method creates a new task.
        It will validate the task and return a success or error message.
        It will also create the tags if they don't exist.
        """

        # Initialize the form with the data
        task_form = CreateNewTaskForm(data)

        # validate the form
        if task_form.is_valid():

            # Get the cleaned data by calling the 'cleaned_data' method
            cleaned_data = task_form.cleaned_data

            # Get the tags from the form data and create them if they don't exist
            tag_objects = TaskManager._create_tags(cleaned_data.get('tags', []))

            # Create the task without saving it yet
            task = CreateNewTaskForm(cleaned_data).save(commit=False)

            # Update tags for the task. This will automatically remove any tags that are not in `tag_objects`
            task.tags.set(tag_objects)

            # Save the task and return feedback
            task.save()
            return True, f"Task '{str(task)}' successfully created!"
        else:
            # error can be a dictionary if more than one error or a string if only one error
            # If the error message is a dictionary, convert it to a string
            if isinstance(task_form.errors, dict):
                error_message = '; '.join([': '.join([key, val[0]]) for key, val in task_form.errors.items()])
            else:
                error_message = task_form.errors

            # return feedback
            return False, error_message

    @staticmethod
    def update_task(task_id, data):
        """
        This method updates an existing task.
        It will first check if the task exists, then use the `EditTaskForm` to validate and update the data.
        Tags associated with the task will be created (if they don't exist) and linked to the task.
        """

        # Check if the task exists
        task = TaskManager._read_task(task_id)
        if not task:
            return False, "The Task does not exist"

        # Use the EditTaskForm to populate the task with the given data
        update_form = EditTaskForm(data, instance=task)

        # Validate the form data
        if update_form.is_valid():

            # get the cleaned data
            cleaned_data = update_form.cleaned_data

            # Get the tags from the form data and create them if they don't exist
            tag_objects = TaskManager._create_tags(cleaned_data.get('tags', []))
            # Update tags for the task. This will automatically remove any tags that are not in `tag_objects`
            task.tags.set(tag_objects)

            # Save the task and return success message
            task = update_form.save()
            return True, f"Task '{str(task)}' successfully created!"
        else:
            return False, update_form.errors

    @staticmethod
    def delete_task(task_id):
        """
        This method deletes an existing task.
        It checks if the task exists, saves the name for feedback, then deletes the task.
        """

        # Check if the task exists
        task = TaskManager._read_task(task_id)
        if not task:
            return False, "Task not found for deletion"

        # Save the task name for feedback
        task_name = task.name

        # Delete the task
        task.delete()

        return True, f"Task '{task_name}' was successfully deleted!"

    @staticmethod
    def list_tasks(tag_filter=None, priority_sort='descending', date_created_sort='ascending'):
        """
        List tasks based on the provided filtering and sorting criteria.
        :param tag_filter: A list of tag names to filter by.
        :param priority_sort: A string indicating how to sort by priority ("ascending" or "descending").
        :param date_created_sort: A string indicating how to sort by creation date ("ascending" or "descending").
        :return: A queryset of matching tasks.
        """

        # Fetch all tasks initially
        tasks = Task.objects.all()

        # Apply tag filter if provided
        if tag_filter:
            tasks = tasks.filter(tags__name__in=tag_filter).distinct()

        # Apply priority sort if provided
        if priority_sort:
            if priority_sort == "ascending":
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
            elif priority_sort == "descending":
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

        # Apply date_created_sort if provided
        if date_created_sort:
            # Assuming that there's a "created_at" field in the Task model
            if date_created_sort == "ascending":
                tasks = tasks.order_by("created_at")
            elif date_created_sort == "descending":
                tasks = tasks.order_by("-created_at")

        return tasks

    ### Utilities Methods ###

    @staticmethod
    def _create_tags(tags):
        """
        Utility method to create or get tags.
        """
        return [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tags]

    @staticmethod
    def _read_task(task_id):
        """
        Utility method reads a task.
        If the task does not exist, it will return None instead of raising an error.
        If the task exists, it will return the task object.
        """
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return None


class HomeView(View):
    """
    This class-based view renders the home page.
    """

    def get(self, request, *args, **kwargs):
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

        # Generate an empty form
        form = CreateNewTaskForm()

        # Get the sorting and view parameters from the URL, if empty, use default values
        priority_sort = request.GET.get('priority_sort', 'priority_ascending')
        current_view = request.GET.get('view', 'list_view')

        # Filter Tags that is in use currently from the database
        used_tags_ids = Task.objects.values_list('tags', flat=True).distinct()
        tags = Tag.objects.filter(id__in=used_tags_ids)

        # Clean up the selected tags passed by the URL
        selected_tags_string = request.GET.get('tags_filter', '')
        selected_tags = selected_tags_string.split(",") if selected_tags_string else []

        # Get the tasks based on the filtering and sorting parameters
        tasks = TaskManager.list_tasks(tag_filter_criteria={"sprint": None},
                                       priority_sort_value=priority_sort,
                                       tag_filter_value=selected_tags)

        # Render the template with the tasks and tags
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

        # Create a new task based on the form data
        form = CreateNewTaskForm(self.request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Create the task
            success, message = TaskManager.create_task(form.cleaned_data)
            # Send success feedback to the user
            tags_list = [str(tag) for tag in form.cleaned_data['tags']]

            return JsonResponse({'status': 'success', 'message': message,
                                 'task': {**form.cleaned_data, 'tags': tags_list}})

        # Send error feedback to the user
        else:
            # If the error message is a dictionary, convert it to a string
            if isinstance(form.errors, dict):  # If errors are returned as a dict
                error_message = '; '.join([': '.join([key, val[0]]) for key, val in form.errors.items()])
            else:
                error_message = form.errors

            return JsonResponse({'status': 'error', 'message': error_message})


class TaskDeleteView(DeleteView):
    """
    This class-based view deletes a task.
    """
    model = Task

    def get(self, *args, **kwargs):
        # TODO: Uncomment this section to enable backend check authenticated user for deletion
        """
        # A simple backend check to ensure user has the right to delete. Adjust as needed.
        if not request.user.has_perm('can_delete_task'):  # Assuming 'can_delete_task' is a permission
            return JsonResponse({
                'status': 'error',
                'message': "You don't have permission to delete this task."
            })
        """

        # Get the task id from the URL
        task_id = self.kwargs.get('pk')  # 'pk' is the default name for the primary key field
        # delete the task can collect feedback
        status, message = TaskManager.delete_task(task_id)
        if status:
            # Send success feedback
            return JsonResponse({'status': 'success', 'message': message})
        else:
            # Send error feedback
            return JsonResponse({'status': 'error', 'message': message})


class EditTaskView(UpdateView):
    """
    This class-based view edits a task.
    """

    def get(self, *args, **kwargs):
        """
        This method renders the edit task page.
        """
        # Get the task id from the URL
        task_id = self.kwargs.get('pk')  # 'pk' is the default name for the primary key field

        # Get the task
        task = TaskManager._read_task(task_id)

        # Check if the task exists
        if not task:
            messages.error(self.request, "Task does not exist")
            return redirect("project_task:project-backlog")

        # Generate a form with the task data
        edit_form = EditTaskForm(instance=task)

        # Render the template with the form
        return render(self.request, "project_task/edit_task.html", {
            "name": "edit-task",
            "edit_form": edit_form,
            "task": task
        })

    def post(self, *args, **kwargs):
        """
        This method handle task edit.
        """

        # Get the task id from the URL
        task_id = self.kwargs.get('pk')  # 'pk' is the default name for the primary key field

        # edit
