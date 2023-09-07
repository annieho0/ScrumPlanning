from django.db import models

# Create your models here.
class ProjectBacklog(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ("STR", "STORY"),
        ("BUG", "BUG"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "LOW"),
        ("MED", "MEDIUM"),
        ("IMP", "IMPORTANT"),
        ("URG", "URGENT"),
    ]

    STATUS_CHOICES = [
        ("NOT", "NOT STARTED"),
        ("IN", "IN PROGRESS"),
        ("COM", "COMPLETED")
    ]

    STAGE_CHOICES = [
        ("PLA", "PLANNING"),
        ("DEV", "DEVELOPMENT"),
        ("TES", "TESTING"),
        ("ITG", "INTEGRATION")
    ]

    name = models.CharField(max_length=200)
    story_point = models.PositiveIntegerField(max_length=10)
    description = models.CharField(max_length=500)

    task_type = models.CharField(max_length=3, choices=TASK_TYPE_CHOICES,  default="ST")
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES)

    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    stage = models.CharField(max_length=3, choices=STAGE_CHOICES)

    project_backlog = models.ForeignKey(ProjectBacklog, on_delete=models.CASCADE)


    def __str__(self):
        return self.name