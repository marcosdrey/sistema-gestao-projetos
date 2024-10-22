from django.urls import path
from . import views


urlpatterns = [
    path('tasks/', views.TaskListView.as_view(), name="task_list"),
    path('tasks/<int:pk>/detail/', views.TaskDetailView.as_view(), name="task_detail"),
    path('tasks/<int:pk>/update/', views.TaskUpdateView.as_view(), name="task_update"),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name="task_delete"),

    path('api/v1/tasks/', views.TaskListCreateAPIView.as_view(), name='task_list_create_api'),
    path('api/v1/tasks/<int:pk>/', views.TaskRetrieveUpdateDestroyAPIView.as_view(), name='task_retrieve_update_destroy_api'),
]
