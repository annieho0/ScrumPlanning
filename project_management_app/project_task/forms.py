from django import forms
from .models import Task, Tag
from django.utils import timezone


class CreateNewTaskForm(forms.ModelForm):
    """
    A form for creating a new task.
    """
    # For the tags, use Django's built-in SelectMultiple widget
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    # Set created_datetime to read-only and set its initial value to current datetime
    created_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'readonly': 'readonly'}),
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
            "created_datetime",
        ]

    def __init__(self, *args, **kwargs):
        super(CreateNewTaskForm, self).__init__(*args, **kwargs)
        self.fields['created_datetime'].initial = timezone.now()


class EditTaskForm(forms.ModelForm):
    """
    A form for editing a task.
    """
    # For the tags, use Django's built-in SelectMultiple widget
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    # Set created_datetime to read-only and set its initial value to current datetime
    created_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'readonly': 'readonly'}),
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
            "sprint",
            "created_datetime",
        ]

    def __init__(self, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)
