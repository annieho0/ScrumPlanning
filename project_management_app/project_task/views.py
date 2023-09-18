from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from .models import Tag, Task
from .forms import CreateNewTaskForm
from django.db.models import Case, When, Value, IntegerField


class TaskManager:
    """
    This class provides methods to manage tasks.
    """

    @staticmethod
    def create_task(data):
        """
        This method creates a new task.
        """
        tags = data.getlist('tags')
        tag_objects = []
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tag_objects.append(tag)

        form = CreateNewTaskForm(data)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            for tag in tag_objects:
                task.tags.add(tag)
            return True, "Task successfully created!"
        else:
            return False, form.errors

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
            return True, "Task successfully updated!"
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
        print("The current view is " + current_view)
        print("The sort_by parameter is " + str(sort_by))
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
            success, message = TaskManager.create_task(self.request.POST)
            if success:
                messages.success(self.request, message)
            else:
                for error in message:
                    messages.error(self.request, message[error][0])
        else:
            # This will handle form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{field}: {error}")
        return redirect('project_backlog')


class TaskDeleteView(DeleteView):
    """
    This class-based view deletes a task.
    """
    model = Task

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'success'})
