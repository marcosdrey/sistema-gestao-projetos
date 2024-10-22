from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, OuterRef, Subquery
from django.utils import timezone
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from projects.models import ProjectMember, Project
from .models import Task
from .forms import TaskForm
from . import serializers


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    template_name = "task_list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        admin_projects = Project.objects.filter(
            members__user=self.request.user,
            members__role='ADMIN',
            id=OuterRef('project__id')
        ).values('id')

        queryset = queryset.annotate(
            is_admin=Subquery(admin_projects)
        ).distinct()

        if not self.request.user.has_perm('tasks.view_task'):
            queryset = queryset.filter(responsible_people=self.request.user)

        title = self.request.GET.get('title')
        priority = self.request.GET.get('priority')
        status = self.request.GET.get('status')
        deadline = self.request.GET.get('deadline')
        project = self.request.GET.get('project')
        state = self.request.GET.get('state')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if project:
            queryset = queryset.filter(project__title__icontains=project)
        if priority:
            queryset = queryset.filter(priority=priority)
        if status:
            queryset = queryset.filter(status=status)
        if deadline:
            queryset = queryset.filter(deadline__lte=deadline)
        if state:
            today = timezone.now().today()
            default_safe_date = today + timezone.timedelta(days=7)
            match state:
                case 'delayed': queryset = queryset.filter(Q(deadline__lt=today) & ~Q(status='DONE'))
                case 'imminent': queryset = queryset.filter(Q(deadline__range=(today, default_safe_date)) & ~Q(status='DONE'))
                case 'plenty-time': queryset = queryset.filter(deadline__gt=default_safe_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['priorities'] = Task._meta.get_field('priority').choices
        context['status'] = Task._meta.get_field('status').choices
        context['current_time'] = timezone.now().date()
        context['imminent_time'] = timezone.now().date() + timezone.timedelta(days=7)
        return context


class TaskDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Task
    template_name = "task_detail.html"
    permission_required = "tasks.view_task"

    def has_permission(self):
        project = self.get_object().project
        if ProjectMember.objects.filter(project=project, user=self.request.user).exists():
            return True
        return self.request.user.has_perm(self.permission_required)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object.project
        is_project_admin = ProjectMember.objects.filter(project=project, user=self.request.user, role='ADMIN').exists()
        context['is_project_admin'] = is_project_admin
        context['current_time'] = timezone.now().date()
        context['imminent_time'] = timezone.now().date() + timezone.timedelta(days=7)
        return context


class TaskUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task_update.html"
    permission_required = "tasks.change_task"

    def has_permission(self):
        project = self.get_object().project
        if ProjectMember.objects.filter(project=project, user=self.request.user, role='ADMIN').exists():
            return True
        return self.request.user.has_perm(self.permission_required)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object and self.object.deadline:
            kwargs['initial'] = {'deadline': self.object.deadline.strftime('%Y-%m-%d')}
        return kwargs

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Task
    template_name = "task_delete.html"
    permission_required = "tasks.change_task"

    def has_permission(self):
        project = self.get_object().project
        if ProjectMember.objects.filter(project=project, user=self.request.user, role='ADMIN').exists():
            return True
        return self.request.user.has_perm(self.permission_required)

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.project.id})


class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.TaskGETSerializer
        return serializers.TaskSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_perm('tasks.view_task'):
            queryset = queryset.filter(responsible_people=self.request.user)
        return queryset

    def perform_create(self, serializer):
        project = self.request.data.get('project')
        is_admin = ProjectMember.objects.filter(project=project, user=self.request.user, role="ADMIN").exists()
        if not is_admin and not self.request.user.has_perm('tasks.add_task'):
            raise ValidationError({"project": "Você não tem permissão para criar tarefas nesse projeto."})
        serializer.save()


class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.TaskGETSerializer
        return serializers.TaskSerializer

    def get_permissions(self):
        if self.request.user.is_authenticated:
            task = get_object_or_404(Task, pk=self.kwargs.get('pk'))
            is_member = ProjectMember.objects.filter(user=self.request.user, project=task.project).exists()
            if is_member:
                return (AllowAny(),)
        return super().get_permissions()

    def perform_update(self, serializer):
        project = self.request.data.get('project')
        is_admin = ProjectMember.objects.filter(project=project, user=self.request.user, role="ADMIN").exists()
        if not is_admin and not self.request.user.has_perm('tasks.change_task'):
            raise ValidationError({"project": "Você não tem permissão para criar tarefas nesse projeto."})
        serializer.save()
