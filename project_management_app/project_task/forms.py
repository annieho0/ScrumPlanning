from django import forms
from .models import Task, Tag, TimeLog
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
            "sprint",
            "created_date",
        ]

    def __init__(self, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)


class TimeLogForm(forms.ModelForm):
    hours_logged = forms.IntegerField(label="Hours", min_value=0)
    class Meta:
        model = TimeLog
        fields = ['hours_logged']
