from datetime import timezone
from django import forms
from .models import Task, Tag
from .models import Sprint
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML


class CreateNewTaskForm(forms.ModelForm):
    """
    A form for creating a new task.

    This form provides fields for creating a new task, including name, type, priority, description,
    story point, tags, stage, and created date. The tags field uses Django's built-in SelectMultiple widget.
    The created date field is set to read-only and its initial value is set to the current datetime.
    """

    # For the tags, use Django's built-in SelectMultiple widget
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    # Set created_date to read-only and set its initial value to current datetime
    created_date = forms.DateField(
        widget=forms.DateInput(attrs={'readonly': 'readonly'}),
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "type",
            "priority",
            "description",
            "story_point",
            "tags",
            "stage",
            "created_date",
        ]

    def __init__(self, *args, **kwargs):
        super(CreateNewTaskForm, self).__init__(*args, **kwargs)
        self.fields['created_date'].initial = timezone.now()


class EditTaskForm(forms.ModelForm):
    """
    A form for editing a task.

    This form provides fields for editing a task, including name, type, priority, description,
    story point, tags, status, stage, assignee, created date, and sprints. The tags field uses
    Django's built-in SelectMultiple widget. The created date field is set to read-only and its
    initial value is set to the current datetime.
    """

    # For the tags, use Django's built-in SelectMultiple widget
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    # Set created_date to read-only and set its initial value to current datetime
    created_date = forms.DateField(
        widget=forms.DateInput(attrs={'readonly': 'readonly'}),
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "type",
            "priority",
            "description",
            "story_point",
            "tags",
            "status",
            "stage",
            "assignee",
            "created_date",
            "sprints",
        ]

    def __init__(self, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)
        self.fields['created_date'].initial = timezone.now()

class CreateNewSprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = [
            "name",
            "start_date",
            "end_date",
        ]

    widgets = {
    'start_date': forms.DateInput(),
    'end_date': forms.DateInput()
    }

    def __init__(self, *args, **kwargs):
        super(CreateNewSprintForm, self).__init__(*args, **kwargs)


class SprintBoardTaskForm(forms.ModelForm):

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "type",
            "priority",
            "description",
            "story_point",
            "tags",
            "status",
            "stage",
            "assignee",
            "created_date",
        ]

    def __init__(self, *args, **kwargs):
        super(SprintBoardTaskForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name not in ["assignee", "status"]:
                self.fields[field_name].disabled = True

class SprintBoardTaskForm(forms.ModelForm):

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "type",
            "priority",
            "description",
            "story_point",
            "tags",
            "status",
            "stage",
            "assignee",
            "created_date",
        ]

    def __init__(self, *args, **kwargs):
        super(SprintBoardTaskForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name not in ["assignee", "status"]:
                self.fields[field_name].disabled = True

class SprintBoardTaskForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "type",
            "priority",
            "description",
            "story_point",
            "tags",
            "status",
            "stage",
            "assignee",
            "created_date",
        ]

    def __init__(self, *args, **kwargs):
        super(SprintBoardTaskForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name not in ["assignee", "status"]:
                self.fields[field_name].disabled = True
