from rest_framework import serializers
from django.db.models import Q
from documents.serializers import DocumentSerializer
from .models import Project, ProjectMember, ProjectComment, ProjectLog


class ProjectMemberGETSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'role']


class ProjectCommentGETSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username')

    class Meta:
        model = ProjectComment
        fields = ['id', 'comment', 'author', 'created_at', 'updated_at']


class ProjectGETSerializer(serializers.ModelSerializer):
    members = ProjectMemberGETSerializer(many=True)
    comments = ProjectCommentGETSerializer(many=True)
    documents = DocumentSerializer(many=True)

    class Meta:
        model = Project
        fields = '__all__'


class ProjectGETSummarizedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'priority', 'status', 'deadline', 'created_at', 'updated_at']


class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = '__all__'


class ProjectLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectLog
        fields = '__all__'


class ProjectCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectComment
        fields = '__all__'
        extra_kwargs = {"author": {"read_only": True}}


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

    def validate_status(self, value):
        if not self.instance and value == 'DONE':
            raise serializers.ValidationError('Um projeto não pode ser inicializado como finalizado.')
        if self.instance and value == 'DONE' and self.instance.tasks.exists():
            pending_tasks = self.instance.tasks.filter(~Q(status='DONE'))
            if pending_tasks.exists():
                raise serializers.ValidationError('Esse projeto contêm tarefas que ainda não foram finalizadas.')
        return value

    def validate_deadline(self, value):
        if self.instance and self.instance.tasks.exists():
            tasks_deadlines = self.instance.tasks.filter(deadline__gt=value)
            if tasks_deadlines.exists():
                raise serializers.ValidationError('O prazo final do projeto não pode ser menor do que o prazo final de nenhuma tarefa')
        return value
