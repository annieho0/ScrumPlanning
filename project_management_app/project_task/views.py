
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic.edit import View
from .models import Tag, Task, Sprint
from .forms import CreateNewTaskForm, EditTaskForm, CreateNewSprintForm, SprintBoardTaskForm
from django.db.models import Case, When, Value, IntegerField
from datetime import timedelta, date, datetime
from django.db import models
from django.utils import timezone
from register.models import CustomizedUser, WorkingHour
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.dateparse import parse_duration
from django.db.models import Sum


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
            task_data = task_form.cleaned_data
            task_data['id'] = new_task.id
            return True, f"Task '{str(new_task)}' successfully created!", task_data
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
        tasks = Task.objects.all().filter(sprints__isnull=True)

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
            'assignee': {'id': task.assignee.id, 'email': task.assignee.email} if task.assignee else None,
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
        for item in tags:
            try:
                # Try to interpret the item as an ID
                tag_id = int(item)
                tag = Tag.objects.get(id=tag_id)
                tag_ids.append(tag.id)
            except (ValueError, Tag.DoesNotExist):
                # If it's not a valid ID or the tag doesn't exist, treat it as a name
                tag, created = Tag.objects.get_or_create(name=item)
                tag_ids.append(tag.id)
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
        create_new_sprint_form = CreateNewSprintForm()
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
            "create_new_sprint_form": create_new_sprint_form,
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
        # TODO: Need to separate this logic into different function or view and use separate URL
        # currently checking if contain element of form
        if 'start_date' in request.POST:
            create_new_sprint_form = CreateNewSprintForm(request.POST)

            if create_new_sprint_form.is_valid():
                create_new_sprint_form.save()
                return redirect('sprint_backlog')
            else:
                return JsonResponse({'status': 'success', 'message': create_new_sprint_form.errors})

        else:
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
        # Check if there is an active sprint
        active_sprints = Sprint.objects.filter(is_completed=False).order_by('start_date')
        if active_sprints.exists():
            first_active_sprint = active_sprints.first()
            return redirect(reverse("sprint_boards", args=[first_active_sprint.pk]),sprint_form)
        else:
            return redirect(reverse("project_backlog"))


        return render(request, self.template_name, {"sprint_form": sprint_form})

    def post(self, request):

        if request.user.is_authenticated:
            # Render and return the home page template with the prepared context
            return render(request, self.template_name)
        else:
            # Render and return the home page template
            return redirect('/login')


class SprintBoard:
    def sprint_boards(request, sprint_id):

        form = SprintBoardTaskForm()

        sprints = Sprint.objects.get(pk=sprint_id)
        sprint = get_object_or_404(Sprint, pk=sprint_id)
        tasks = Task.objects.filter(sprints=sprints)
        backlog_tasks = Task.objects.filter(sprints=None)
        # Fetch unique tags associated with tasks
        tags = Tag.objects.filter(task__isnull=False).distinct()
        statuses = [('NOT', 'Incomplete'), ('IN_PROG', 'In Progress'), ('COM', 'Complete')]
        if sprint.is_completed:
        # Delete tasks that are not completed and associated with the archived sprint
            tasks = tasks.filter(status='COM')
        return render(request, "project_task/sprint_board.html", {"name": "sprint-board", "tasks": tasks, "statuses": statuses, "tags": tags,"backlog_tasks": backlog_tasks, 'sprint_id': sprint_id, 'sprint': sprint, 'form': form})

    def move_selected_tasks(request):
        # Handle the selection and moving of tasks to the sprint board
        if request.method == 'POST':
            selected_tasks = request.POST.getlist('selected_tasks')  # extract the list of selected tasks
            sprint_id = request.POST.get('sprint_id')  # extract the sprint id
            for task_id in selected_tasks:  # loop through the list of selected tasks
                task = get_object_or_404(Task, pk=task_id)  # TODO: need error handling redundancy here if task does not exist
                task.sprints.add(sprint_id)
                task.save()
        return redirect('sprint_boards', sprint_id=sprint_id)

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
    
    def get_total_hours(request, task_id):
        try:
            # Filter WorkingHour objects based on task 
            total_hours = WorkingHour.objects.filter(task_id=task_id).aggregate(Sum('hour'))['hour__sum']

            if total_hours is not None:
                return JsonResponse({'status': 'success', 'message': 'Total hours retrieved successfully', 'total_hours': total_hours.total_seconds() / 3600})
            else:
                return JsonResponse({'status': 'success', 'message': 'No hours found for the given task and person', 'total_hours': 0.0})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get_task_data(request, task_id):
        # Fetch the task details using the TaskManager utility
        status, message, task_data = TaskManager.get_task_details(task_id)
        
        # If the task was successfully fetched, send a success response
        if status:
            total_hours = WorkingHour.objects.filter(task_id=task_id).aggregate(Sum('hour'))['hour__sum']
            total_hours_in_hours = total_hours.total_seconds() if total_hours is not None else 0.0

            # You can add total_hours_in_hours to the task_data dictionary
            task_data['total_hour'] = total_hours_in_hours

            return JsonResponse({'status': 'success', 'message': message, 'task_data': task_data})

        # If the task wasn't found or there was an issue, send an error response
        return JsonResponse({'status': 'error', 'message': message, 'task_data': task_data})


    def edit_tasks(request, task_id):
        if request.method == 'POST':
            tasks = Task.objects.get(pk=task_id)
    
            # Retrieve the assignee's user ID from the POST data
            assignee_id = request.POST.get('assignee')

            # Get the CustomizedUser instance corresponding to the user ID
            if assignee_id is not None:
                assignee = get_object_or_404(CustomizedUser, pk=assignee_id)
            else:
                assignee = None

            tasks.assignee = assignee
            tasks.status = request.POST.get('status')
            if tasks.status == Task.COMPLETED and not tasks.completed_date:
                tasks.completed_date = timezone.now().date()

            hour_str = request.POST.get('hour')
            time = parse_duration(hour_str)

            
            person = request.user

            # Update the WorkingHour instance associated with the task
            working_hour, created = WorkingHour.objects.get_or_create(
                task=tasks,
                person=person, 
                date = timezone.now(),
                hour = time,
            )
            working_hour.hour = time
            working_hour.save()

            tasks.save()
            

            updated_task = {
                'assignee': tasks.assignee.username,
                'status': tasks.status,
                'hour': str(working_hour.hour)
            }

            return JsonResponse({'message': 'Task updated successfully', 'updated_task': updated_task})
        else:
            return JsonResponse({'message': 'Invalid request method'}, status=400)



    # def edit_task(request, task_id):
    #     if request.method == 'POST':
    #         task = Task.objects.get(pk=task_id)
    #         task.assignee = request.POST.get('assignee')
    #         task.status = request.POST.get('status')
    #         task.save()
            
    #         updated_task = {
    #             'assignee': task.assignee,
    #             'status': task.status,
    #         }

    #         print('Task updated successfully:', updated_task)  # Debugging statement

    #         return JsonResponse({'message': 'Task updated successfully', 'updated_task': updated_task})
    #     else:
    #         return JsonResponse({'message': 'Invalid request method'}, status=400)


class CreateGraph:
    """
       class for creating graphs
    """
    template_name = 'create_graph.html'

    @staticmethod
    def accumulated_hours_data(sprint):
        start_date = sprint.start_date
        end_date = sprint.end_date

        accumulated_hours_per_day = []
        total_hours = 0.0
        current_date = start_date

        while current_date <= end_date:
            # Filter tasks by the current date and accumulate the hours logged for that day
            hours_logged_today = WorkingHour.objects.filter(task__sprints=sprint, date=current_date).aggregate(
                sum_hours=Sum('hour'))['sum_hours'] or timedelta()
            total_hours += hours_logged_today.total_seconds()
            accumulated_hours_per_day.append(total_hours)
            current_date += timedelta(days=1)

        return accumulated_hours_per_day

    @staticmethod
    def remaining_effort_data(sprint):
        start_date = sprint.start_date
        end_date = sprint.end_date

        remaining_points_per_day = []
        total_story_points = Task.objects.filter(sprints=sprint).aggregate(total=Sum('story_point'))['total'] or 0

        current_date = start_date

        while current_date <= end_date:
            points_burned_today = \
                Task.objects.filter(sprints=sprint, status=Task.COMPLETED, completed_date=current_date).aggregate(
                    total=Sum('story_point'))['total'] or 0

            total_story_points -= points_burned_today

            remaining_points_per_day.append(total_story_points)

            current_date += timedelta(days=1)

        return remaining_points_per_day

    @staticmethod
    def ideal_effort_data(sprint, total_story_points):
        num_days_in_sprint = (sprint.end_date - sprint.start_date).days + 1
        if num_days_in_sprint == 1:
            ideal_decrease_per_day = total_story_points  # Or however you want to handle this special case
        else:
            ideal_decrease_per_day = total_story_points / (num_days_in_sprint - 1)
        ideal_effort = [total_story_points - i * ideal_decrease_per_day for i in range(num_days_in_sprint)]
        return ideal_effort

    @staticmethod
    def create_graph(request, sprint_id):
        sprint = get_object_or_404(Sprint, pk=sprint_id)
        # Fetch accumulated hours for the given sprint
        accumulated_hours = CreateGraph.accumulated_hours_data(sprint)

        remaining_effort = CreateGraph.remaining_effort_data(sprint)

        total_story_points = Task.objects.filter(sprints=sprint).aggregate(total=Sum('story_point'))['total'] or 0

        ideal_effort = CreateGraph.ideal_effort_data(sprint, total_story_points)

        # Calculate the number of days in the sprint
        num_days_in_sprint = (sprint.end_date - sprint.start_date).days + 1

        days = ["Day {}".format(i + 1) for i in range(num_days_in_sprint)]

        context = {
            "days": days,
            "remaining_effort": remaining_effort,
            "accumulated_hours": accumulated_hours,
            "ideal_effort": ideal_effort,
        }
        return render(request, 'project_task/create_graph.html', context)
