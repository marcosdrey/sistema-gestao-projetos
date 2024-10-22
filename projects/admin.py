from django.contrib import admin
from .models import Project, ProjectComment, ProjectMember, ProjectLog


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'deadline', 'created_at')
    search_fields = ('title',)
    list_filter = ('priority', 'status')


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'author', 'created_at', 'updated_at')
    search_fields = ('project', 'author')


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role')
    search_fields = ('project', 'user')
    list_filter = ('role',)


@admin.register(ProjectLog)
class ProjectLogAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'description', 'created_at')
    search_fields = ('project',)
