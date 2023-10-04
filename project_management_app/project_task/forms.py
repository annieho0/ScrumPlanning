from datetime import timezone
from django import forms
from .models import Task, Tag, Sprint 
from .models import Sprint
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
            "created_date",
            "assignee",
            # "sprint",
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
            "created_date",
            "sprints",
        ]

    def __init__(self, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)

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






