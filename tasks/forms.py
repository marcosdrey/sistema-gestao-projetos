from django import forms
from django.contrib.auth.models import User
from projects.models import Project
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'responsible_people': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'project': forms.HiddenInput()
        }
        labels = {
            'title': 'Título',
            'priority': 'Prioridade',
            'status': 'Status',
            'deadline': 'Prazo',
            'responsible_people': 'Responsáveis',
            'description': 'Descrição',
        }

    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id', None)
        super().__init__(*args, **kwargs)

        if project_id is not None:
            self.fields['project'].initial = project_id

    def clean_deadline(self):
        if self.instance.pk:
            project = self.instance.project
        else:
            project = self.cleaned_data.get("project")

        task_deadline = self.cleaned_data.get("deadline")
        try:
            if project and task_deadline:
                if not isinstance(project, Project):
                    project = Project.objects.get(pk=project)
                if task_deadline > project.deadline:
                    self.add_error("deadline", f"O prazo da tarefa não pode ser maior do que o prazo final do projeto ({project.deadline.strftime('%d/%m/%Y')})")
        except Project.DoesNotExist:
            self.add_error("deadline", "O projeto especificado não existe")

        return task_deadline

    def clean_responsible_people(self):
        if self.instance.pk:
            project = self.instance.project
        else:
            project = self.cleaned_data.get("project")

        task_responsible_people = self.cleaned_data.get("responsible_people")
        try:
            if project and task_responsible_people:
                if not isinstance(project, Project):
                    project = Project.objects.get(pk=project)
                task_responsible_people_ids = [user.id for user in task_responsible_people]
                project_members_ids = [user.user.id for user in project.members.all()]
                not_allowed_users = [User.objects.get(pk=user_id).username for user_id in task_responsible_people_ids if user_id not in project_members_ids]
                if not_allowed_users:
                    self.add_error("responsible_people", f"O(s) seguinte(s) usuário(s) não estão no projeto: {', '.join(not_allowed_users)}")
        except Project.DoesNotExist:
            self.add_error("responsible_people", "O projeto especificado não existe")
        return task_responsible_people

    def clean_project(self):
        project = self.cleaned_data.get('project')
        if project:
            if project.status == 'DONE':
                raise forms.ValidationError("Não é possível criar ou editar tarefas para um projeto que está concluído.")
        return project
