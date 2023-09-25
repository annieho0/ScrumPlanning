from django import forms
from .models import Task, Tag
from register.models import CustomizedUser

class CreateNewTaskForm(forms.ModelForm):
    """
    A form for creating a new task.
    """
    # users = CustomizedUser.objects.all()
    # users_choices = []
    # for user in users:
    #     users_choices.append((user, user.get_name()))

    # For the tags, use Django's built-in SelectMultiple widget
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        # widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True,
    )
    
    assignee = forms.ModelChoiceField(
        queryset=CustomizedUser.objects.all(),
        # widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True,
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