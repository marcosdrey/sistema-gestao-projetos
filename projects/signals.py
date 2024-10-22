from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import Project, ProjectComment, ProjectMember, ProjectLog
from .middleware import get_current_user


old_instance = {}
project_being_del = {}


@receiver(pre_save, sender=Project)
def store_old_project_instance(sender, instance, **kwargs):
    if Project.objects.filter(pk=instance.id).exists():
        old_instance[instance.pk] = Project.objects.get(pk=instance.id)


@receiver(post_save, sender=Project)
def project_create_log(sender, instance, created, **kwargs):
    user = get_current_user()
    description = f"'{user.username}' criou o projeto {instance}."

    if not created and instance.pk in old_instance:
        changed_fields = []
        for field in old_instance[instance.pk]._meta.fields:
            if field.name != 'updated_at':
                old_instance_value = getattr(old_instance[instance.pk], field.name)
                current_instance_value = getattr(instance, field.name)
                if old_instance_value != current_instance_value:
                    changed_fields.append(field.name)
        description = f"'{user.username}' editou o(s) seguinte(s) campo(s): {', '.join(field for field in changed_fields)}."

    ProjectLog.objects.create(
        user=user,
        project=instance,
        description=description
    )


@receiver(post_save, sender=ProjectMember)
def project_member_saved_create_log(sender, instance, created, **kwargs):
    project_object_manage_log(instance, created)


@receiver(post_delete, sender=ProjectMember)
def project_member_deleted_create_log(sender, instance, **kwargs):
    if project_being_del.get(instance.project.pk) is None:
        project_object_manage_log(instance, is_deletion=True)
        project_tasks = instance.project.tasks.all()
        for task in project_tasks:
            if instance.user in task.responsible_people.all():
                task.responsible_people.remove(instance.user)


@receiver(post_save, sender=ProjectComment)
def project_comment_saved_create_log(sender, instance, created, **kwargs):
    project_object_manage_log(instance, created)


@receiver(post_delete, sender=ProjectComment)
def project_comment_deleted_create_log(sender, instance, **kwargs):
    if project_being_del.get(instance.project.pk) is None:
        project_object_manage_log(instance, is_deletion=True)


def project_object_manage_log(instance, created=None, is_deletion=False):
    request_user = get_current_user()

    action = "removeu" if is_deletion else "adicionou" if created else "editou"

    if isinstance(instance, ProjectMember):
        description = f"'{request_user}' {action} o usuário '{instance.user}' no projeto."
    elif isinstance(instance, ProjectComment):
        description = f"'{request_user}' {action} um comentário no projeto."

    ProjectLog.objects.create(
        user=request_user,
        project=instance.project,
        description=description
    )


@receiver(pre_delete, sender=Project)
def project_being_deleted(sender, instance, **kwargs):
    project_being_del[instance.pk] = True
