from django.contrib import admin
from .models import Hostel


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('name', 'incharge', 'capacity', 'created_on', 'updated_on')
    list_filter = ('created_on', 'updated_on', 'capacity')
    search_fields = ('name', 'incharge__name', 'wardens__name', 'remarks')
    ordering = ('-created_on',)
    autocomplete_fields = ('incharge', 'wardens')
    filter_horizontal = ('wardens',)
    date_hierarchy = 'created_on'
    readonly_fields = ('created_on', 'updated_on')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'incharge', 'wardens', 'capacity', 'remarks')
        }),
        ('Timestamps', {
            'fields': ('created_on', 'updated_on'),
            'classes': ('collapse',)
        }),
    )
