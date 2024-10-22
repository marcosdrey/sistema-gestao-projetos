from django.urls import path
from . import views


urlpatterns = [
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/detail/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    path('projects/<int:pk>/new-member/', views.ProjectMemberCreateView.as_view(), name='project_member_create'),
    path('projects/update-member/<int:pk>/', views.ProjectMemberUpdateView.as_view(), name='project_member_update'),
    path('projects/delete-member/<int:pk>/', views.ProjectMemberDeleteView.as_view(), name='project_member_delete'),

    path('projects/<int:pk>/new-comment/', views.ProjectCommentCreateView.as_view(), name='project_comment_create'),
    path('projects/update-comment/<int:pk>/', views.ProjectCommentUpdateView.as_view(), name='project_comment_update'),
    path('projects/delete-comment/<int:pk>/', views.ProjectCommentDeleteView.as_view(), name='project_comment_delete'),

    path('projects/<int:pk>/new-task/', views.ProjectTaskCreateView.as_view(), name="project_task_create"),


    path('api/v1/projects/', views.ProjectListCreateAPIView.as_view(), name='project_list_create_api'),
    path('api/v1/projects/<int:pk>/', views.ProjectRetrieveUpdateDestroyAPIView.as_view(), name='project_retrieve_update_destroy_api'),

    path('api/v1/projects/new-member/', views.ProjectMemberCreateAPIView.as_view(), name='projectmember_create_api'),
    path('api/v1/projects/new-comment/', views.ProjectCommentCreateAPIView.as_view(), name='projectcomment_create_api'),
    path('api/v1/projects/members/<int:pk>/', views.ProjectMemberRetrieveUpdateDestroyAPIView.as_view(), name='projectmember_retrieve_update_destroy_api'),
    path('api/v1/projects/comments/<int:pk>/', views.ProjectCommentRetrieveUpdateDestroyAPIView.as_view(), name='projectcomment_retrieve_update_destroy_api'),

    path('api/v1/projects/<int:pk>/logs/', views.ProjectLogListAPIView.as_view(), name='projectlog_list_api')
]
