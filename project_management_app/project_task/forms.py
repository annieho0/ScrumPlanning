from datetime import timezone
from django import forms
from .models import Sprint
from .models import Task, Tag, TimeLog, Sprint
from django.utils import timezone


class CreateNewTaskForm(forms.ModelForm):
    """
    A form for creating a new task.
    """
    # Hidden field to determine form type
    form_type = forms.CharField(initial='task', widget=forms.HiddenInput(), required=False)

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
            "sprint",
            "form_type", #hidden field
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


class CreateNewSprintForm(forms.ModelForm):
    """
    A form for creating a sprint
    """
    # Hidden field to determine form type
    form_type = forms.CharField(initial='sprint', widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Sprint
        fields = [
            "name",
            "start_date",
            "end_date",
            "form_type",
        ]

    widgets = {
        'start_date': forms.DateInput(),
        'end_date': forms.DateInput()
    }

    def __init__(self, *args, **kwargs):
        super(CreateNewSprintForm, self).__init__(*args, **kwargs)

# class SprintBoard (forms.ModelForm):
# tags = forms.ModelMultipleChoiceField(
# queryset=Tag.objects.all(),
# widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
# required=True
# )
# class Meta:
# model = SprintBoard
# fields = [
# "name"
# "tags"
# "assignee"
# "story_point"
#  ]

# class EditSprintBoard (forms.ModelForm):
# class Meta:
# model = SprintBoard
# fields = ['assignee']
