from django.contrib import admin
from .models import Email

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'timestamp', 'read', 'archived')
    list_filter = ('read', 'archived', 'timestamp')
    search_fields = ('user__username', 'subject', 'body')
