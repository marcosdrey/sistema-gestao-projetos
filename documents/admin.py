from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
