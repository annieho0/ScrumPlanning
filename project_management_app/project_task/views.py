from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import View
from .models import Tag, Task, Sprint
from .forms import CreateNewTaskForm, EditTaskForm, CreateNewSprintForm 
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone


class TaskManager:
    """
    Utility class for managing tasks.
    Provides static methods to handle task-related operations like creation, updation, deletion, and fetching details.
    """

    @staticmethod
    def create_task(response_data):
        """
        Creates a new task based on the provided data.

        Parameters:
            response_data (dict): The data for the new task.

        Returns:
            tuple: A tuple containing:
                - bool: Status of the task creation (True if successful, False otherwise).
                - str: Success or error message.
                - dict or None: Cleaned data from the form if the task was successfully created, None otherwise.
        """

        # Create tags and get their IDs
        tag_ids = TaskManager._create_tags(response_data.getlist('tags'))

        # Create a mutable copy of response_data since Django QueryDict is immutable
        mutable_data = response_data.copy()

        # Update the tags in mutable_data with their corresponding IDs
        mutable_data.setlist('tags', tag_ids)

        # Initialize the form with the modified data
        task_form = CreateNewTaskForm(mutable_data)

        # Validate the form
        if task_form.is_valid():
            # Create the task without saving it yet
            new_task = task_form.save(commit=False)

            # Save the task to the database
            new_task.save()
            task_form.save_m2m()
            return True, f"Task '{str(new_task)}' successfully created!", task_form.cleaned_data
        else:
            # Convert the error messages to a string format
            error_message = '; '.join([': '.join([key, val[0]]) for key, val in task_form.errors.items()])
            return False, error_message, None

    @staticmethod
    def update_task(task_id, response_data):
        """
        Updates an existing task based on the provided data.

        Parameters:
            task_id (int): The ID of the task to be updated.
            response_data (dict): The updated data for the task.

        Returns:
            tuple: A tuple containing:
                - bool: Status of the task update (True if successful, False otherwise).
                - str: Success or error message.
                - dict or None: Cleaned data from the form if the task was successfully updated, None otherwise.
        """

        # Check if the task exists
        task = TaskManager._read_task(task_id)
        if not task:
            return False, "The Task does not exist"

        # Create tags and get their IDs
        tag_ids = TaskManager._create_tags(response_data.getlist('tags'))

        # Create a mutable copy of response_data since Django QueryDict is immutable
        mutable_data = response_data.copy()

        # Update the tags in mutable_data with their corresponding IDs
        mutable_data.setlist('tags', tag_ids)

        # Use the EditTaskForm to populate the task with the given data
        update_form = EditTaskForm(mutable_data, instance=task)

        # Validate the form data
        if update_form.is_valid():

            # Create the task without saving it yet
            updated_task = update_form.save(commit=False)

            # Save the task and return feedback
            # Save the task and return feedback
            # Now save the task to DB
            updated_task.save()
            update_form.save_m2m()

            # Get the task details as dictionary
            task_details = TaskManager.get_task_details(task_id)

            return True, f"Task '{str(updated_task)}' successfully updated!", task_details
            
        else:
            return False, update_form.errors, None

    @staticmethod
    def delete_task(task_id):
        """
        This method deletes an existing task.
        It checks if the task exists, saves the name for feedback, then deletes the task.

        Parameters:
            task_id (int): The ID of the task to be deleted.

        Returns:
            tuple: A tuple containing:
                - bool: Status of the task deletion (True if successful, False otherwise).
                - str: Success or error message.
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
    def list_tasks(tag_filter=None, priority_sort=None, date_created_sort=None):
        """
        List tasks based on the provided filtering and sorting criteria.

        Parameters:
            tag_filter (list of str, optional): A list of tag names to filter by.
            priority_sort (str, optional): A string indicating how to sort by priority ("ascending" or "descending").
            date_created_sort (str, optional): A string indicating how to sort by creation date ("ascending" or "descending").

        Returns:
            QuerySet: A queryset of matching tasks.
        """

        # Fetch all tasks initially
        tasks = Task.objects.all()

        # Apply tag filter if provided
        if tag_filter:
            tasks = tasks.filter(tags__name__in=tag_filter).distinct()

        # Define priority mapping
        priority_mapping = {
            'LOW': 0,
            'MED': 1,
            'IMP': 2,
            'URG': 3
        }

        # Create a list of ordering criteria
        order_by_list = []

        # Apply priority sort if provided
        if priority_sort:
            priority_ordering = Case(
                *[When(priority=key, then=Value(value)) for key, value in priority_mapping.items()],
                output_field=IntegerField()
            )
            if priority_sort == "priority_ascending":
                order_by_list.append(priority_ordering)
            elif priority_sort == "priority_descending":
                order_by_list.append(priority_ordering.desc())  # Use .desc() for descending

        # Apply date_created_sort if provided
        if date_created_sort:
            if date_created_sort == "date_ascending":
                order_by_list.append('created_date')
            elif date_created_sort == "date_descending":
                order_by_list.append('-created_date')

        # Apply the ordering criteria
        tasks = tasks.order_by(*order_by_list)

        return tasks

    @staticmethod
    def get_task_details(task_id):
        """
        This method fetches the details of a specific task given its ID.
        If the task exists, it will return its details as a dictionary.
        If the task does not exist, it will return None.

        Parameters:
            task_id (int): The ID of the task to fetch details for.

        Returns:
            tuple: A tuple containing:
                - bool: Status of the task retrieval (True if found, False otherwise).
                - str: Success or error message.
                - dict or None: Task details as a dictionary if the task was found, None otherwise.
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
            # 'sprint': task.sprint,
            'created_date': task.created_date,
            # ... add any other necessary fields here ...
        }

        return True, f'Fetching Task {task_id}', task_details

    ### Utilities Methods ###

    @staticmethod
    def _create_tags(tags):
        """
        Utility method to create or retrieve tags.
        For each tag in the provided list, the method checks if it exists in the database.
        If it doesn't exist, the tag gets created. If it does, the tag is simply retrieved without changes.

        Parameters:
            tags (list of str): A list of tag names to either create or retrieve.

        Returns:
            tag_ids (list of str): A list of processed tag IDs.
        """
        tag_ids = []
        for tag_name in tags:
            # Check if the tag exists in the database, if not, create it
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tag_ids.append(tag.id)  # Append the tag ID to the list
        return tag_ids


    @staticmethod
    def _read_task(task_id):
        """
        Utility method to retrieve a task based on its ID.

        Parameters:
            task_id (int): The ID of the task to fetch.

        Returns:
            Task or None: Returns the Task object if found. If the task doesn't exist, returns None.
        """
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return None


class TaskListView(View):
    """
    View class for the project backlog page.

    Handles operations related to listing tasks in the product backlog and creating new tasks.
    Attributes:
        template_name (str): Path to the HTML template for the project backlog page.
    """

    template_name = 'project_task/project_backlog.html'

    def get(self, request):
        """
        Handles GET requests to render the product backlog page.

        Fetches tasks based on filtering and sorting parameters from the URL, generates forms for task creation and
        editing, and prepares the context for the template rendering.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: Rendered project backlog page with tasks and relevant context.
        """

        # Generate an empty CreateNewTask form and EditTask form
        create_new_task_form = CreateNewTaskForm()
        edit_task_form = EditTaskForm()

        # Extract sorting, view, and date created sort parameters from the URL or use default values
        priority_sort = request.GET.get('priority_sort', 'priority_ascending')
        current_view = request.GET.get('view', 'list_view')
        date_sort = request.GET.get('date_sort', 'date_ascending')

        # Retrieve tags that are currently in use
        used_tags_ids = Task.objects.values_list('tags', flat=True).distinct()
        tags = Tag.objects.filter(id__in=used_tags_ids)

        # Process the selected tags passed via the URL
        selected_tags_string = request.GET.get('tags_filter', '')
        selected_tags = selected_tags_string.split(",") if selected_tags_string else []

        # Fetch tasks based on filtering and sorting parameters using TaskManager utility
        tasks = TaskManager.list_tasks(tag_filter=selected_tags, priority_sort=priority_sort, date_created_sort=date_sort)

        # Construct the context for the template
        context = {
            "name": "project-backlog",
            "create_new_task_form": create_new_task_form,
            "edit_task_form": edit_task_form,
            "tasks": tasks,
            "tags": tags,
            "current_view": current_view,
            "priority_sort": priority_sort,
            "selected_tags": selected_tags,
            "date_sort": date_sort,
        }

        # Render and return the template with the prepared context
        return render(request, self.template_name, context)

    def post(self, request):
        """
        Handles POST requests for creating a new task.

        Validates the form data, creates the task using TaskManager utility, and responds with a JSON containing the
        task details or error message.

        Parameters:
            request (HttpRequest): The HTTP request object containing form data.

        Returns:
            JsonResponse: A JSON response indicating the success or failure of task creation.
        """

        # Attempt to create a new task using the TaskManager utility
        success, message, task_details = TaskManager.create_task(request.POST)

        # Handle unsuccessful task creation (e.g., form validation errors)
        if not success:
            return JsonResponse({'status': 'error', 'message': message})

        # Convert task tags into a list of strings
        tags_list = [str(tag) for tag in task_details['tags']]

        # Respond with a JSON indicating successful task creation and task details
        return JsonResponse({'status': 'success', 'message': message, 'task': {**task_details, 'tags': tags_list}})


class TaskEditView(View):
    """
    View class for the task edit page.

    Handles operations related to editing tasks in the product backlog and updating them.

    Attributes:
        template_name (str): Path to the HTML template for the task edit page.
    """

    template_name = 'project_task/edit_task.html'

    def get(self, request, task_id):
        """
        Handles GET requests to fetch details of a specific task for editing.

        This method retrieves the details of the task, prepares the data, and sends a JSON response.

        Parameters:
            request (HttpRequest): The HTTP request object.
            task_id (int): The ID of the task to be fetched for editing.

        Returns:
            JsonResponse: A JSON response containing the task details or an error message.
        """

        # Fetch the task details using the TaskManager utility
        status, message, task_data = TaskManager.get_task_details(task_id)

        # If the task was successfully fetched, send a success response
        if status:
            return JsonResponse({'status': 'success', 'message': message, 'task_data': task_data})

        # If the task wasn't found or there was an issue, send an error response
        return JsonResponse({'status': 'error', 'message': message, 'task_data': task_data})

    def post(self, request, task_id):
        """
        Handles POST requests to update a task's details.

        This method validates the form data, updates the task using TaskManager utility, and responds with a JSON
        indicating the success or failure of the update.

        Parameters:
            request (HttpRequest): The HTTP request object containing updated task data.
            task_id (int): The ID of the task to be updated.

        Returns:
            JsonResponse: A JSON response indicating the success or failure of task update.
        """

        # Attempt to update the task using the TaskManager utility
        success, message, task_data = TaskManager.update_task(task_id, request.POST)

        # If the task was successfully updated, send a success response
        if success:
            return JsonResponse({'status': 'success', 'message': message, 'task_data': task_data})

        # If there were issues during the update (e.g., form validation errors), send an error response
        return JsonResponse({'status': 'error', 'message': message})


class TaskDeleteView(View):
    """
    View class for handling task deletion operations in the product backlog page.
    """

    def post(self, request, task_id):
        """
        Handles POST requests to delete a specific task.

        This method utilizes the TaskManager utility to delete the task and sends a JSON response indicating
        the success or failure of the operation.

        Parameters:
            request (HttpRequest): The HTTP request object.
            task_id (int): The ID of the task to be deleted.

        Returns:
            JsonResponse: A JSON response indicating the success or failure of task deletion.
        """

        # Attempt to delete the task using the TaskManager utility
        success, message = TaskManager.delete_task(task_id)

        # If the task was successfully deleted, send a success response
        if success:
            return JsonResponse({'status': 'success', 'message': message})

        # If there was an issue during deletion, send an error response
        return JsonResponse({'status': 'error', 'message': message})


class HomeListView(View):
    """
    View class for rendering the home page of the project task application.

    Attributes:
        template_name (str): Path to the HTML template for the home page.
    """

    template_name = 'project_task/home.html'

    def get(self, request):
        """
        Handles GET requests to render the home page.

        This method prepares the context (if necessary) and renders the home page template.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: Rendered home page with any relevant context.
        """
        sprint_form = CreateNewSprintForm()
    
        return render(request, self.template_name, {"sprint_form": sprint_form})

    def post(self,request):
        """
        Handles POST requests to create a new sprint.

        This method validates the form data, creates the sprint, and redirects to the Sprint Backlog page upon success.

        Parameters:
            request (HttpRequest): The HTTP request object containing sprint data.

        Returns:
            HttpResponse: Redirects to the Sprint Backlog page upon success or renders the home page with errors.
        """
        sprint_form = CreateNewSprintForm(request.POST)

        if sprint_form.is_valid():
            sprint = sprint_form.save()
            return redirect('sprint_backlog')
        else:
            print("Form is not valid:", sprint_form.errors)
            return render(request, "project_task/sprint_backlog.html", {"sprint_form": sprint_form})


class SprintBoard():


    # def sprint_board(request):
    #     """This view renders the project backlog page"""
    #     tasks = Task.objects.filter()
    #     # Fetch unique tags associated with tasks
    #     tags = Tag.objects.filter(task__isnull=False).distinct()
    #     statuses = [('NOT', 'Incomplete'), ('IN_PROG', 'In Progress'), ('COM', 'Complete')]
    #     return render(request, "project_task/sprint_board.html", {"name": "sprint-board", "tasks": tasks, "statuses": statuses, "tags": tags})
    
    def sprint_boards(request, sprint_id):
        sprints = Sprint.objects.get(pk=sprint_id)
        sprint = get_object_or_404(Sprint, pk=sprint_id)
        tasks = Task.objects.filter(sprints=sprints)
        # Fetch unique tags associated with tasks
        tags = Tag.objects.filter(task__isnull=False).distinct()
        statuses = [('NOT', 'Incomplete'), ('IN_PROG', 'In Progress'), ('COM', 'Complete')]
        if sprint.is_completed:
        # Delete tasks that are not completed and associated with the archived sprint
            task = tasks.filter(status='COM')
        return render(request, "project_task/sprint_board.html", {"name": "sprint-board", "tasks": task, "statuses": statuses, "tags": tags})
    

    # def redirect_to_sprint_board(request, sprint_id):
    #     return redirect('sprint_boards', sprint_id=sprint_id)

    def active_sprints(request):
        # Get all active sprints
        active_sprints = Sprint.objects.filter(end_date__gt=timezone.now(), is_completed=False)

        # Get all completed sprints
        completed_sprints = Sprint.objects.filter(end_date__lte=timezone.now(), is_completed=False)

        # Update completed sprints and move them to the archived sprints
        for sprint in completed_sprints:
            sprint.is_completed = True
            sprint.save()

        # Get the sprint backlog (only active sprints)
        sprint_backlog = active_sprints

        return render(request, 'project_task/sprint_backlog.html', {'sprint_backlog': sprint_backlog})

    def archived_sprints(request):
        sprint_backlog_archived = Sprint.objects.filter(is_completed=True)
        return render(request, 'project_task/sprint_backlog_archived.html', {'sprint_backlog_archived': sprint_backlog_archived})

    def archive_sprint_backlog(request, sprint_id):
        try:
            sprint = get_object_or_404(Sprint, id=sprint_id)
            
            if not sprint.is_completed:
                # If the sprint is not completed, set the end_date to today
                sprint.end_date = timezone.now()
            
            sprint.is_completed = True  # Mark the sprint as completed
            
            sprint.save()
            
        except Sprint.DoesNotExist:
            # Handle the case where the sprint does not exist
            pass

        # Redirect back to the Sprint Backlog page after archiving
        return redirect('sprint_backlog')
    

    def update_task(request, task_id):

        if request.method == 'POST':
            task_name = request.POST.get('name')
            task_assignee = request.POST.get('assignee')
            task_status = request.POST.get('status')

        try:
            task = get_object_or_404(Task, pk=task_id)
            task.name = task_name
            task.assignee = task_assignee
            task.status = task_status
            task.save()
            success = True
        except Task.DoesNotExist:
            success = False

        return JsonResponse({'success': success})
    
 