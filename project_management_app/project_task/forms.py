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
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super(CreateNewTaskForm, self).__init__(*args, **kwargs)