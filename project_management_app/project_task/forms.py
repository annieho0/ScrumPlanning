from django import forms
from .models import Task, Tag


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
        ]

    def __init__(self, *args, **kwargs):
        super(CreateNewTaskForm, self).__init__(*args, **kwargs)


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

    # set created_date to read-only
    created_date = forms.DateTimeField(disabled=True)

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
            "created_date",
        ]

    def __init__(self, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)
