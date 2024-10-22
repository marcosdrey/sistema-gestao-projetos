from django.urls import path
from . import views


urlpatterns = [
    path('documents/', views.DocumentListView.as_view(), name='document_list'),
    path('documents/new/', views.DocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/detail/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:pk>/update/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),

    path('api/v1/documents/', views.DocumentListCreateAPIView.as_view(), name='document_list_create_api'),
    path('api/v1/documents/<int:pk>/', views.DocumentRetrieveUpdateDestroyAPIView.as_view(), name='document_retrieve_update_destroy_api'),
]
