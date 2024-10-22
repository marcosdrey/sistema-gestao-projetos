import json
from django.db.models import Count, Q
from django.utils import timezone
from projects.models import Project, ProjectLog
from tasks.models import Task
from documents.models import Document


def _get_total_object_by_status(obj):
    status_dict = {choice[0]: 0 for choice in obj._meta.get_field('status').choices}

    status_count = obj.objects.values('status').annotate(total=Count('id'))
    for status in status_count:
        status_dict[status['status']] = status['total']

    status_dict['TOTAL'] = sum(status_dict.values())
    return status_dict


def _get_total_object_by_priority(obj):
    priority_choices = obj._meta.get_field('priority').choices
    priority_dict = {choice[1]: 0 for choice in priority_choices}

    priority_count = obj.objects.values('priority').annotate(total=Count('id'))
    for priority in priority_count:
        for choice in priority_choices:
            if priority['priority'] == choice[0]:
                priority_dict[choice[1]] = priority['total']
    return json.dumps(priority_dict)


def _get_total_delayed_object(obj):
    return obj.objects.filter(Q(deadline__lt=timezone.now().today()) & ~Q(status='DONE')).count()


def _get_total_imminent_object(obj):
    today = timezone.now().today()
    limit_date = today + timezone.timedelta(days=7)
    return obj.objects.filter(Q(deadline__range=(today, limit_date)) & ~Q(status='DONE')).count()


def get_total_projects_by_status():
    return _get_total_object_by_status(Project)


def get_total_projects_by_priority():
    return _get_total_object_by_priority(Project)


def get_total_delayed_projects():
    return _get_total_delayed_object(Project)


def get_total_imminent_projects():
    return _get_total_imminent_object(Project)


def get_daily_total_projects_logs():
    today = timezone.now().date()
    dates = [str(today - timezone.timedelta(days=i)) for i in range(6, -1, -1)]
    values = []

    for date in dates:
        log_count = ProjectLog.objects.filter(created_at__date=date).count()
        values.append(log_count)

    return json.dumps(dict(
        dates=dates,
        values=values
    ))


def get_total_tasks_by_status():
    return _get_total_object_by_status(Task)


def get_total_tasks_by_priority():
    return _get_total_object_by_priority(Task)


def get_total_delayed_tasks():
    return _get_total_delayed_object(Task)


def get_total_imminent_tasks():
    return _get_total_imminent_object(Task)


def get_projects_with_most_pending_tasks():
    allowed_status = ('TO_DO', 'DEVELOPING', 'PAUSED')
    projects_with_task_count = Project.objects.annotate(task_count=Count('tasks', filter=Q(tasks__status__in=allowed_status))).order_by('-task_count')[:3]
    project_map = {project.title: project.task_count for project in projects_with_task_count}

    return json.dumps(project_map)


def get_total_docs():
    return Document.objects.all().count()


def get_most_used_docs():
    docs_most_used_count = Document.objects.annotate(project_count=Count('projects')).order_by('-project_count')[:3]
    docs_map = {doc.name: doc.project_count for doc in docs_most_used_count}

    return json.dumps(docs_map)


def get_less_used_docs():
    docs_less_used_count = Document.objects.annotate(project_count=Count('projects')).order_by('project_count')[:3]
    docs_map = {doc.name: doc.project_count for doc in docs_less_used_count}

    return json.dumps(docs_map)


def get_calendar_data():
    tasks = Task.objects.exclude(status='DONE', deadline__lte=timezone.now().today())
    projects = Project.objects.exclude(status='DONE', deadline__lte=timezone.now().today())

    calendar_data = [
        {'title': task.title, 'deadline': task.deadline.strftime('%Y-%m-%d'), 'color': '#ff9f00'}
        for task in tasks
    ]

    calendar_data.extend([
        {'title': project.title, 'deadline': project.deadline.strftime('%Y-%m-%d'), 'color': '#F50101'}
        for project in projects
    ])

    return json.dumps(calendar_data)
