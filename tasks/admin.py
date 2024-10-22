from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'priority', 'status', 'deadline', 'created_at', 'updated_at')
    search_fields = ('title', 'project')
    list_filter = ('priority', 'status')
