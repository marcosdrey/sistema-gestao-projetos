from django import forms
from django.db.models import Q
from .models import Project, ProjectMember


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'documents': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'title': 'Título',
            'description': 'Descrição',
            'documents': 'Documentos',
            'priority': 'Prioridade',
            'status': 'Status',
            'deadline': 'Prazo'
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if instance is None:
            self.fields['status'].choices = [
                choice for choice in Project._meta.get_field('status').choices if choice[0] != 'DONE'
            ]

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if self.instance.pk and status == 'DONE' and self.instance.tasks.exists():
            pending_tasks = self.instance.tasks.filter(~Q(status='DONE'))
            if pending_tasks.exists():
                self.add_error('status', 'Esse projeto contêm tarefas que ainda não foram finalizadas.')
        return status

    def clean_deadline(self):
        proj_deadline = self.cleaned_data.get('deadline')
        if self.instance.pk and self.instance.tasks.exists():
            tasks_deadlines = self.instance.tasks.filter(deadline__gt=proj_deadline)
            if tasks_deadlines.exists():
                self.add_error('deadline', 'O prazo final do projeto não pode ser menor do que o prazo final de nenhuma tarefa')
        return proj_deadline


class ProjectMemberForm(forms.ModelForm):
    class Meta:
        model = ProjectMember
        fields = ['user', 'role']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'user': 'Usuário',
            'role': 'Função'
        }
