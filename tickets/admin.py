from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'status', 'assignee', 'created_by', 'created_at', 'completed_at')
    list_filter = ('team', 'status', 'assignee')
    search_fields = ('title', 'description')
