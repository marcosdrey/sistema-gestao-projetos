from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
from documents.models import Document
from core import constants


class Project(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    documents = models.ManyToManyField(Document, related_name='projects', blank=True)
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


class ProjectMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    role = models.CharField(max_length=50, choices=constants.ROLE_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'], name='unique_user_project')
        ]
        ordering = [models.Case(
            models.When(role='ADMIN', then=0),
            models.When(role='MEMBER', then=1),
            default=2,
            output_field=models.IntegerField()
        )]

    def __str__(self):
        return self.user.username


class ProjectComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_comments")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.author.username


class ProjectLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_logs")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="logs")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.project.title
