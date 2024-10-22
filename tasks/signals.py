from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from projects.middleware import get_current_user
from projects.models import ProjectLog
from projects.signals import project_being_del
from .models import Task


@receiver(post_save, sender=Task)
def project_task_saved_create_log(sender, instance, created, **kwargs):
    project_task_manage_log(instance, created)


@receiver(post_delete, sender=Task)
def project_task_deleted_create_log(sender, instance, **kwargs):
    if project_being_del.get(instance.project.id) is None:
        project_task_manage_log(instance, is_deletion=True)


def project_task_manage_log(instance, created=None, is_deletion=False):
    request_user = get_current_user()

    action = "removeu" if is_deletion else "adicionou" if created else "editou"

    description = f"'{request_user}' {action} a tarefa '{instance.title}' no projeto."

    ProjectLog.objects.create(
        user=request_user,
        project=instance.project,
        description=description
    )
