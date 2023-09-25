from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Task(models.Model):
    """
    A model for a task that consist of all the required and non required information.
    """

    # Choices for the task type.
    STORY = 'STORY'
    BUG = 'BUG'
    TYPE_CHOICES = [
        (STORY, "STORY"),
        (BUG, "BUG")
    ]

    # Choices for the task priority.
    LOW = 'LOW'
    MEDIUM = 'MED'
    IMPORTANT = 'IMP'
    URGENT = 'URG'
    PRIORITY_CHOICES = [
        (LOW, "LOW"),
        (MEDIUM, "MEDIUM"),
        (IMPORTANT, "IMPORTANT"),
        (URGENT, "URGENT")
    ]

    # Choices for the task status.
    NOT_STARTED = 'NOT'
    IN_PROGRESS = 'IN_PROG'
    COMPLETED = 'COM'
    STATUS_CHOICES = [
        (NOT_STARTED, "NOT STARTED"),
        (IN_PROGRESS, "IN PROGRESS"),
        (COMPLETED, "COMPLETED")
    ]

    # Choices for the task stage.
    PLANNING = 'PLA'
    DEVELOPMENT = 'DEV'
    TESTING = 'TES'
    INTEGRATION = 'ITG'
    STAGE_CHOICES = [
        (PLANNING, "PLANNING"),
        (DEVELOPMENT, "DEVELOPMENT"),
        (TESTING, "TESTING"),
        (INTEGRATION, "INTEGRATION")
    ]

    # Fields for the Task model.
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    type = models.CharField(max_length=5, choices=TYPE_CHOICES, default=STORY)
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default=NOT_STARTED)
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES)
    stage = models.CharField(max_length=3, choices=STAGE_CHOICES)
    tags = models.ManyToManyField('Tag', blank=False, null=False)
    story_point = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], null=True,
                                              blank=True)
    # TODO: Assignee is a string for now. Need to connect to user model to get the user name in future sprint
    assignee = models.CharField(max_length=200, null=True, blank=True)
    # TODO: Sprint is a string for now. Need to connect to sprint model to get the sprint name in future sprint
    sprint = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    A model for a tag that can be associated with a task.
    """
    name = models.CharField(max_length=100, unique=True)  # Name of the tag (e.g., front-end, back-end, testing).

    def __str__(self):
        return self.name

class Sprint(models.Model):
    """
    A model for a Sprint.
    """
    name = models.CharField(max_length=200, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name