from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import metrics


@login_required
def home(request):
    context = {
        'total_projects_by_status': metrics.get_total_projects_by_status(),
        'total_projects_by_priority': metrics.get_total_projects_by_priority(),
        'daily_total_projects_logs': metrics.get_daily_total_projects_logs(),
        'total_delayed_projects': metrics.get_total_delayed_projects(),
        'total_imminent_projects': metrics.get_total_imminent_projects(),

        'total_tasks_by_status': metrics.get_total_tasks_by_status(),
        'total_tasks_by_priority': metrics.get_total_tasks_by_priority(),
        'total_delayed_tasks': metrics.get_total_delayed_tasks(),
        'total_imminent_tasks': metrics.get_total_imminent_tasks(),
        'projects_with_most_pending_tasks': metrics.get_projects_with_most_pending_tasks(),

        'total_docs': metrics.get_total_docs(),
        'most_used_docs': metrics.get_most_used_docs(),
        'less_used_docs': metrics.get_less_used_docs(),

        'calendar_data': metrics.get_calendar_data()
    }

    return render(request, 'home.html', context)
