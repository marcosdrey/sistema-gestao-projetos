import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Document


@receiver(pre_save, sender=Document)
def remove_old_file(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Document.objects.get(pk=instance.pk)
            if old_instance.file.path != instance.file.path and os.path.isfile(old_instance.file.path):
                os.remove(old_instance.file.path)
        except Document.DoesNotExist:
            raise Exception('O documento não existe.')


@receiver(post_delete, sender=Document)
def remove_file(sender, instance, **kwargs):
    if os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
