from django.db import models


class Document(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='docs/')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
