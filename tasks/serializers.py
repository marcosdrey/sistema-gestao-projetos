from rest_framework import serializers
from django.contrib.auth.models import User
from projects.models import Project
from .models import Task


class TaskGETSerializer(serializers.ModelSerializer):
    responsible_people = serializers.SerializerMethodField()
    project = serializers.CharField(source='project.title')

    class Meta:
        model = Task
        fields = '__all__'

    def get_responsible_people(self, obj):
        return [user.username for user in obj.responsible_people.all()]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def validate_deadline(self, value):
        project = self.initial_data.get("project")
        try:
            project = Project.objects.get(pk=project)
            if value > project.deadline:
                raise serializers.ValidationError(f"O prazo da tarefa não pode ser maior do que o prazo final do projeto ({project.deadline.strftime('%d/%m/%Y')})")
        except Project.DoesNotExist:
            raise serializers.ValidationError("Esse projeto não existe.")
        return value

    def validate_responsible_people(self, value):
        project = self.initial_data.get("project")
        try:
            project = Project.objects.get(pk=project)
            task_responsible_people_ids = [user.id for user in value]
            project_members_ids = [user.user.id for user in project.members.all()]
            not_allowed_users = [User.objects.get(pk=user_id).username for user_id in task_responsible_people_ids if user_id not in project_members_ids]
            if not_allowed_users:
                raise serializers.ValidationError(f"O(s) seguinte(s) usuário(s) não estão no projeto: {', '.join(not_allowed_users)}")
        except Project.DoesNotExist:
            raise serializers.ValidationError("Esse projeto não existe.")
        return value

    def validate_project(self, value):

        if value.status == 'DONE':
            raise serializers.ValidationError("Não é possível criar ou editar tarefas para um projeto que está concluído.")
        return value
