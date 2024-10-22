from django.urls import reverse_lazy
from rest_framework import generics
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Document
from .forms import DocumentForm
from .serializers import DocumentSerializer


class DocumentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Document
    context_object_name = 'documents'
    template_name = 'document_list.html'
    permission_required = 'documents.view_document'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class DocumentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'document_create.html'
    permission_required = 'documents.add_document'

    def get_success_url(self):
        return reverse_lazy('document_detail', kwargs={'pk': self.object.pk})


class DocumentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Document
    template_name = 'document_detail.html'
    permission_required = 'documents.view_document'


class DocumentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'document_update.html'
    permission_required = 'documents.change_document'

    def get_success_url(self):
        return reverse_lazy('document_detail', kwargs={'pk': self.object.pk})


class DocumentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Document
    template_name = 'document_delete.html'
    permission_required = 'documents.delete_document'

    def get_success_url(self):
        return reverse_lazy('document_list')


class DocumentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
