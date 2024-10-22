from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from projects.models import Project
from core import constants


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    responsible_people = models.ManyToManyField(User, related_name="tasks", blank=True)
    title = models.CharField(max_length=300)
    description = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=50, choices=constants.PRIORITY_CHOICES)
    status = models.CharField(max_length=50, choices=constants.STATUS_CHOICES)
    deadline = models.DateField(validators=[
        MinValueValidator(timezone.now().date(), 'A data de término deve ser maior que a data atual.')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            models.Case(
                models.When(status='DONE', then=models.Value(1)),
                models.When(status='TO_DO', then=models.Value(0)),
                models.When(status='PAUSED', then=models.Value(0)),
                models.When(status='DEVELOPING', then=models.Value(0)),
                output_field=models.IntegerField(),
            ), 'deadline', 'title']

    def __str__(self):
        return self.title
