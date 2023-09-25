from django import forms
from .models import Task, Tag
from .models import Sprint


class CreateNewTaskForm(forms.ModelForm):
    """
    A form for creating a new task.
    """
    # For the tags, use Django's built-in SelectMultiple widget
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "type",
            "priority",
            "description",
            "story_point",
            "assignee",
            "tags",
            "status",
            "stage",
        ]

    def __init__(self, *args, **kwargs):
        super(CreateNewTaskForm, self).__init__(*args, **kwargs)

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