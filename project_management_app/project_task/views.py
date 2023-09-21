from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.edit import View
from .models import Tag, Task
from .forms import CreateNewTaskForm, EditTaskForm
from django.db.models import Case, When, Value, IntegerField


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

    @staticmethod
    def get_task_details(task_id):
        """
        This method fetches the details of a specific task given its ID.
        If the task exists, it will return its details as a dictionary.
        If the task does not exist, it will return None.
        """

        # Fetch the task object using the provided ID
        task = TaskManager._read_task(task_id)
        if not task:
            return False, f"Task {task_id} not found", None

        # Convert the task details to a dictionary
        task_details = {
            'id': task.id,
            'name': task.name,
            'description': task.description,
            'type': task.type,
            'priority': task.priority,
            'stage': task.stage,
            'tags': [tag.name for tag in task.tags.all()],
            'story_point': task.story_point,
            'assignee': task.assignee,
            'status': task.status,
            'sprint': task.sprint,
            # ... add any other necessary fields here ...
        }

        return True, f'Fetching Task {task_id}', task_details

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


class TaskListView(View):
    """
    This view handles listing tasks and create new ones in product backlog page.
    """
    template_name = 'project_task/project_backlog.html'

    def get(self, request):
        """
        This method handles GET requests to the view for Listing tasks.
        It will fetch the tasks and other filter/sort context for listing, then render the template.
        """

        # Generate an empty form
        create_new_task_form = CreateNewTaskForm()

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

        # Create the context for the template
        context = {
            "name": "project-backlog",
            "tasks": tasks,
            "tags": tags,  # Pass the tags to the template
            "form": create_new_task_form,
            "current_view": current_view,  # Pass the current view to the template
            "priority_sort": priority_sort,  # Pass the sort_by parameter to the template
            "selected_tags": selected_tags  # Pass the selected tags to the template
        }

        # Render the template with the tasks and tags
        return render(request, self.template_name, context)

    def post(self, request):
        """
        This method handles POST requests to the view for Creating new tasks.
        It will validate the form, create the task, and return a JSON response.
        This does not render a template (refresh the page). Front-end JS will handle the addition of the task to UI.
        """

        # Use the TaskManager.create_task method to create the task
        success, message = TaskManager.create_task(request.POST)

        # If form validation failed or there was an error during task creation
        if not success:
            return JsonResponse({'status': 'error', 'message': message})

        # If task creation was successful
        return JsonResponse({'status': 'success', 'message': message})


class TaskEditView(View):
    """
    This view handles editing tasks and updating it in the product backlog page.
    """
    template_name = 'project_task/edit_task.html'

    def get(self, request, task_id):
        """
        This method handles GET requests to the view to populate the form for editing tasks.
        """

        # Use the TaskManager to update the task
        status, message, task_data = TaskManager.get_task_details(task_id)

        # If the task does not exist, return an error message
        if status:
            return JsonResponse({'status': 'success', 'message': message, 'task_data': task_data})
        else:
            return JsonResponse({'status': 'error', 'message': message, 'task_data': task_data})

    def post(self, request, task_id):
        """
        This method handles POST requests to the view for Updating tasks.
        """

        # Use the TaskManager to update the task
        success, message = TaskManager.update_task(task_id, request.POST)

        if success:
            return JsonResponse({'status': 'success', 'message': message})

        # If form validation failed or there was an error during task update
        return JsonResponse({'status': 'error', 'message': message})


class TaskDeleteView(View):
    """
    This view handles deleting tasks and updating it in the product backlog page.
    """

    def post(self, request, task_id):
        """
        This method handles POST requests to the view for Deleting tasks.
        """

        # Use the TaskManager to update the task
        success, message = TaskManager.delete_task(task_id)

        if success:
            return JsonResponse({'status': 'success', 'message': message})

        # If form validation failed or there was an error during task update
        return JsonResponse({'status': 'error', 'message': message})


class HomeListView(View):
    """
    This view handles rendering the home page.
    """
    template_name = 'project_task/home.html'

    def get(self, request):
        """
        This method handles GET requests to the view for rendering the home page.
        """

        # Render the template
        return render(request, self.template_name)


