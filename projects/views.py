import json
from django.db.models import Q, OuterRef, Subquery
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from rest_framework import generics
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from core.permissions import DenyAny
from tasks.models import Task
from tasks.forms import TaskForm
from .models import Project, ProjectMember, ProjectComment
from .forms import ProjectForm, ProjectMemberForm
from . import serializers


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = 'projects'
    template_name = 'project_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        member_projects = Project.objects.filter(
            members__user=self.request.user,
            id=OuterRef('id')
        ).values('id')

        admin_projects = member_projects.filter(
            members__user=self.request.user,
            members__role='ADMIN',
            id=OuterRef('id')
        ).values('id')

        queryset = queryset.annotate(
            is_member=Subquery(member_projects),
            is_admin=Subquery(admin_projects)
        ).distinct()

        title = self.request.GET.get('title')
        priority = self.request.GET.get('priority')
        status = self.request.GET.get('status')
        deadline = self.request.GET.get('deadline')
        state = self.request.GET.get('state')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if priority:
            queryset = queryset.filter(priority=priority)
        if status:
            queryset = queryset.filter(status=status)
        if deadline:
            queryset = queryset.filter(deadline__lte=deadline)
        if state:
            today = timezone.now().today()
            default_safe_date = today + timezone.timedelta(days=7)
            if state == 'delayed':
                queryset = queryset.filter(Q(deadline__lt=today) & ~Q(status='DONE'))
            elif state == 'imminent':
                queryset = queryset.filter(Q(deadline__range=(today, default_safe_date)) & ~Q(status='DONE'))
            elif state == 'plenty-time':
                queryset = queryset.filter(deadline__gt=default_safe_date)

        return queryset.order_by(Project._meta.ordering[0], '-is_admin', '-is_member')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['priorities'] = Project._meta.get_field('priority').choices
        context['status'] = Project._meta.get_field('status').choices
        context['current_time'] = timezone.now().date()
        context['imminent_time'] = timezone.now().date() + timezone.timedelta(days=7)
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_paginator = Paginator(self.object.logs.all(), 10)
        log_page_number = self.request.GET.get('log_page')
        log_page = log_paginator.get_page(log_page_number)

        comment_paginator = Paginator(self.object.comments.all(), 3)
        comment_page_number = self.request.GET.get('comment_page')
        comment_page = comment_paginator.get_page(comment_page_number)

        tasks_list = self.object.tasks.all()
        calendar_tasks = [
            {'title': task.title, 'deadline': task.deadline.strftime('%Y-%m-%d'), 'color': '#ff9f00'}
            for task in tasks_list
        ]
        calendar_tasks.append({'title': 'Fim do projeto', 'deadline': self.object.deadline.strftime('%Y-%m-%d'), 'color': '#F50101'})

        is_project_member = self.object.members.filter(user=self.request.user).exists()
        is_project_admin = self.object.members.filter(user=self.request.user, role='ADMIN').exists()

        context['log_page'] = log_page
        context['comment_page'] = comment_page
        context['calendar_tasks'] = json.dumps(calendar_tasks)
        context['is_project_member'] = is_project_member
        context['is_project_admin'] = is_project_admin
        context['current_time'] = timezone.now().date()
        context['imminent_time'] = timezone.now().date() + timezone.timedelta(days=7)
        return context


class ProjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_create.html'
    permission_required = 'projects.add_project'

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_update.html'
    permission_required = 'projects.change_project'

    def has_permission(self):
        if ProjectMember.objects.filter(project=self.get_object(), user=self.request.user, role='ADMIN').exists():
            return True
        return self.request.user.has_perm(self.permission_required)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object and self.object.deadline:
            kwargs['initial'] = {'deadline': self.object.deadline.strftime('%Y-%m-%d')}
        return kwargs

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Project
    template_name = 'project_delete.html'
    permission_required = 'projects.delete_project'

    def get_success_url(self):
        return reverse_lazy('project_list')


class ProjectMemberCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ProjectMember
    form_class = ProjectMemberForm
    template_name = "project_member_create.html"
    permission_required = "projects.add_projectmember"

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        form.instance.project = Project.objects.get(pk=self.kwargs['pk'])
        if ProjectMember.objects.filter(user=form.instance.user, project=form.instance.project).exists():
            form.add_error('user', 'Esse usuário já está incluso no projeto.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return context


class ProjectMemberUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ProjectMember
    form_class = ProjectMemberForm
    template_name = "project_member_update.html"
    permission_required = "projects.change_projectmember"

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.project.id})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('user', None)
        return form


class ProjectMemberDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ProjectMember
    template_name = "project_member_delete.html"
    permission_required = "projects.delete_projectmember"

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.project.id})


class ProjectCommentCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'projects.add_projectcomment'

    def has_permission(self):
        if ProjectMember.objects.filter(project__id=self.kwargs.get('pk'), user=self.request.user).exists():
            return True
        return self.request.user.has_perm(self.permission_required)

    def post(self, request, *args, **kwargs):
        author = request.user
        project_id = self.kwargs.get('pk')
        project = get_object_or_404(Project, pk=project_id)
        comment = request.POST.get('comment')
        if len(comment) > 0:
            ProjectComment.objects.create(
                author=author,
                project=project,
                comment=comment
            )
        return redirect('project_detail', project_id)


class ProjectCommentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):

    def get_object(self):
        project_comment_id = self.kwargs.get('pk')
        return get_object_or_404(ProjectComment, pk=project_comment_id)

    def has_permission(self):
        project_comment = self.get_object()
        return self.request.user == project_comment.author

    def get(self, request, *args, **kwargs):
        return render(request, 'project_comment_update.html', {'object': self.get_object()})

    def post(self, request, *args, **kwargs):
        project_comment = self.get_object()
        comment = request.POST.get('comment')
        if len(comment) > 0:
            project_comment.comment = comment
            project_comment.save()
        return redirect('project_detail', project_comment.project.id)


class ProjectCommentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ProjectComment
    template_name = "project_comment_delete.html"
    permission_required = "projects.delete_projectcomment"

    def has_permission(self):
        project_comment = self.get_object()
        return self.request.user == project_comment.author or self.request.user.has_perm(self.permission_required)

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.project.id})


class ProjectTaskCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "project_task_create.html"
    permission_required = 'tasks.add_task'

    def has_permission(self):
        if ProjectMember.objects.filter(project__id=self.kwargs.get('pk'), user=self.request.user, role='ADMIN').exists():
            return True
        return self.request.user.has_perm(self.permission_required)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project_id'] = self.kwargs.get('pk')
        return kwargs

    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_id'] = self.kwargs.get('pk')
        return context


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    queryset = Project.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.ProjectGETSummarizedSerializer
        return serializers.ProjectSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return (IsAuthenticated(),)
        return super().get_permissions()


class ProjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()

    def get_serializer_class(self):
        member = ProjectMember.objects.filter(user=self.request.user, project=self.get_object())

        if self.request.method in SAFE_METHODS:
            if member.exists() or self.request.user.has_perm('projects.view_project'):
                return serializers.ProjectGETSerializer
            return serializers.ProjectGETSummarizedSerializer

        return serializers.ProjectSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return (IsAuthenticated(),)
        if self.request.user.is_authenticated:
            project = get_object_or_404(Project, pk=self.kwargs.get('pk'))
            is_admin = ProjectMember.objects.filter(user=self.request.user, project=project, role='ADMIN').exists()
            if is_admin:
                return (AllowAny(),) if self.request.method != 'DELETE' else (DenyAny(),)
        return super().get_permissions()


class ProjectMemberCreateAPIView(generics.CreateAPIView):
    queryset = ProjectMember.objects.all()
    serializer_class = serializers.ProjectMemberSerializer


class ProjectCommentCreateAPIView(generics.CreateAPIView):
    queryset = ProjectComment.objects.all()
    serializer_class = serializers.ProjectCommentSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        project = self.request.data.get('project')
        is_member = ProjectMember.objects.filter(project=project, user=self.request.user).exists()
        if not is_member and not self.request.user.has_perm('projects.add_projectcomment'):
            raise ValidationError({"project": "Você não tem permissão para comentar nesse projeto."})
        serializer.save(author=self.request.user)


class ProjectMemberRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectMember.objects.all()
    serializer_class = serializers.ProjectMemberSerializer


class ProjectCommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectComment.objects.all()
    serializer_class = serializers.ProjectCommentSerializer

    def perform_update(self, serializer):
        project = self.request.data.get('project')
        if project:
            is_member = ProjectMember.objects.filter(project=project, user=self.request.user).exists()
            if not is_member:
                raise ValidationError({"project": "Você não tem permissão para comentar nesse projeto."})
        serializer.save(author=self.request.user)

    def get_permissions(self):
        projectcomment = get_object_or_404(ProjectComment, pk=self.kwargs.get('pk'))
        is_the_author = projectcomment.author == self.request.user

        print(is_the_author)
        if is_the_author:
            return (AllowAny(),)

        print('furou')
        if self.request.method in ('PATCH', 'PUT'):
            return (DenyAny(),)
        return super().get_permissions()


class ProjectLogListAPIView(generics.ListAPIView):
    serializer_class = serializers.ProjectLogSerializer

    def get_queryset(self):
        project_pk = self.kwargs.get('pk')
        project = get_object_or_404(Project, pk=project_pk)
        return project.logs.all()

    def get_permissions(self):
        if self.request.user.is_authenticated:
            project = get_object_or_404(Project, pk=self.kwargs.get('pk'))
            is_admin = ProjectMember.objects.filter(user=self.request.user, role='ADMIN', project=project).exists()
            if is_admin:
                return (AllowAny(),)
        return super().get_permissions()
